import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from kinconnect_api.config import load_dotenv, PROCESSED_DATA_DIR
from langchain_core.messages import HumanMessage
from langchain_fireworks import ChatFireworks
from langchain_core.pydantic_v1 import BaseModel, Field
from kinconnect_api.db import get_vector_store, get_mongo_client, get_profile_by_name
from kinconnect_api.llm_utils import call_fireworks_api_no_structure, call_fireworks_api_with_structure, FIREFUNC_MODEL, MISTRAL_MODEL, LLAMA_70B_MODEL

import pandas as pd

load_dotenv()

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

QUERY_PROMPT: str = """I have a request to match with a database of engineers, designers, project managers etc. This request in the form of answers to two questions. 

Each profile in database includes their skills, projects, career history, and interests. 
The goal is to expand this request into one cohesive ask to ensure it captures all relevant aspects and nuances needed for accurate matching. 

Here is the request in question answer pairs:

# Query Context
"{context}"

Please expand this request to include additional relevant details, such as specific skills, roles, project types, and any other contextual information that would improve the accuracy of matching with the profiles in the database. Consider what someone might need in a hackathon context, including complementary skills, leadership qualities, and relevant experience. This request will be used to do semantic search on the database. So the description and content of the request is very very crucial for accuracy.

Respond in <expanded_request> xml tags. The request should have all the answers and details. No yapping. No other text."""

REWRITE_SUMMARY_QUERY_OLD: str = '''
Understand the request and rewrite it in a easy to understand manner. Make sure to capture all the details. Write in 2 paragraphs like a formal and professional tone. Describe technologies, skills and details in specific details.

Request: {context}
'''

REWRITE_SUMMARY_QUERY: str = '''
Understand the request and extract the critical skills and technologies required. Make sure to capture all the details.

No yapping. Just state the critical skills and technologies required.
Request: {context}
'''

def extract_answer_from_submission(question: str, form_submission: str) -> Optional[Dict[str, str]]:
    """
    Extracts the answer to a specific question from the form submission.

    Args:
        question (str): The question to search for in the form submission.
        form_submission (str): The form submission text.

    Returns:
        Optional[Dict[str, str]]: A dictionary containing the question and its answer, or None if not found.
    """
    pattern = re.compile(rf"{re.escape(question)}\n(.*?)\n##", re.DOTALL)
    match = pattern.search(form_submission)

    if match:
        answer = match.group(1)
        return {
            "question": question,
            "answer": answer
        }
    else:
        logging.info("Question not found or no answer available.")
        return None

def create_profile_matching_request(profile: Dict[str, Any]) -> Optional[str]:
    """
    Creates a profile matching request based on the given profile.

    Args:
        profile (Dict[str, Any]): The profile containing form submission data.

    Returns:
        Optional[str]: The expanded query string or None if an error occurred.
    """
    form_submission: str = profile['form_submission']
    people_to_meet: Optional[Dict[str, str]] = extract_answer_from_submission(
        question="## Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?",
        form_submission=form_submission
    )
    project_idea: Optional[Dict[str, str]] = extract_answer_from_submission(
        question="## If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.",
        form_submission=form_submission
    )

    if not people_to_meet or not project_idea:
        logging.error("Failed to extract necessary information from form submission.")
        return None

    context: str = f"""Topic: {people_to_meet['question']}
        Request: {people_to_meet['answer']}

        Topic: {project_idea['question']}
        Request: {project_idea['answer']}"""
    
    expanded_request: Optional[str] = generate_expanded_request(context)
    if expanded_request is None:
        return None

    expanded_query_string: Optional[str] = summarize_expanded_request(expanded_request)
    return expanded_query_string

def generate_expanded_request(context: str) -> Optional[str]:
    """
    Generates an expanded request using the given context.

    Args:
        context (str): The context to use for generating the expanded request.

    Returns:
        Optional[str]: The expanded request or None if an error occurred.
    """
    rewrite_query_prompt: str = QUERY_PROMPT.format(context=context)
    response: Dict[str, Optional[Any]] = call_fireworks_api_no_structure(rewrite_query_prompt, MISTRAL_MODEL)
    if response['error']:
        logging.error("Failed to generate expanded request.")
        return None
    return response['output']

def summarize_expanded_request(expanded_request: str) -> Optional[str]:
    """
    Summarizes the expanded request.

    Args:
        expanded_request (str): The expanded request to summarize.

    Returns:
        Optional[str]: The summarized expanded request or None if an error occurred.
    """
    summary_prompt: str = REWRITE_SUMMARY_QUERY.format(context=expanded_request)
    response: Dict[str, Optional[Any]] = call_fireworks_api_no_structure(summary_prompt, LLAMA_70B_MODEL)
    if response['error']:
        logging.error("Failed to summarize expanded request.")
        return None
    logging.info(f'Summarized expanded request: {response["output"]}')
    return response['output']


def get_match_summary_explanation(expanded_request: str, profile: Dict[str, Any]) -> Optional[str]:
    """
    Get the summary explanation for a match.
    """
    summary_explain_prompt_template = '''
    You are given a detailed, expanded query and a matched profile of an engineer. Your task is to generate a summary explanation that highlights why the profile is a good match for the query. The summary should include key points about the engineer's skills, experiences, and projects that align with the needs and goals outlined in the query. Ensure that the explanation is clear, concise, and compelling, emphasizing the most relevant aspects of the match.

    List the critical skills required based on the expanded query.
    If the profile is missing critical skills, respond with "BAD MATCH".

    Expanded Query:

    Copy code
    {expanded_query}
    Matched Profile:

    Copy code
    {matched_profile}

    Your response should be technical, consise and fun to read. It should be no more than 100 words. No yapping.
    <critical_skills> tags should be used to list the critical skills required.
    Enclose your response in <summary> tags.
    '''
    summary_explain_prompt = summary_explain_prompt_template.format(expanded_query=expanded_request, matched_profile=profile['form_submission'])
    response: Dict[str, Optional[Any]] = call_fireworks_api_no_structure(summary_explain_prompt, LLAMA_70B_MODEL)
    class SummaryExplanation(BaseModel):
        summary: str = Field(description="The summary explanation for a matched profile to the request.")
    structure_parse_prompt = f'''
    You are given a response from an LLM. Your task is to parse the response and return the summary explanation.
    Response:
    {response}
    '''
    summary_response = call_fireworks_api_with_structure(structure_parse_prompt, SummaryExplanation, FIREFUNC_MODEL)
    return summary_response['output']['summary']

def get_match_profiles(query_text: str) -> List[Dict[str, Any]]:
    """
    Retrieves matching profiles based on the query text.

    Args:
        query_text (str): The query text to search for matching profiles.

    Returns:
        List[Dict[str, Any]]: A list of matching profiles.
    """
    vector_store = get_vector_store()
    documents_with_scores = vector_store.similarity_search_with_score(query_text, k=5)
    profile_names = [doc.metadata['name'] for doc, score in documents_with_scores]
    client = get_mongo_client()
    profiles = list(client.kinconnect.profiles.find({'name': {'$in': profile_names}}))
    return profiles

def get_matches_for_profile_with_name(name: str) -> Optional[pd.DataFrame]:
    """
    Retrieves matching profiles for a given profile name.

    Args:
        name (str): The name of the profile to find matches for.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing the matching profiles or None if no matches found.
    """
    profile = get_profile_by_name(name)
    if not profile:
        logging.error(f"No profile found with name: {name}")
        return None
    query_string = create_profile_matching_request(profile)
    if not query_string:
        logging.error("Failed to create profile matching request.")
        return None
    profile_matches = get_match_profiles(query_string)
    profile_matches = [match for match in profile_matches if match.get('name') != name]
    df = pd.DataFrame(profile_matches)
    df['summary_explanation'] = df.apply(lambda row: get_match_summary_explanation(expanded_request=query_string, profile=row), axis=1)
    df = df[~df['summary_explanation'].str.contains('BAD MATCH', case=False, na=False)].drop(columns=['_id', 'form_submission'])
    return df

def main() -> None:
    """
    Main function to generate synthetic data by calling multiple API-driven Gen AI endpoints.
    """
    profile_name = "Nehil Jain (TEST)"
    matches_df = get_matches_for_profile_with_name(profile_name)
    sanitized_filename = re.sub(r'[^a-zA-Z0-9]', '_', f'matches_{profile_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    matches_df.to_parquet(f'{PROCESSED_DATA_DIR}/{sanitized_filename}.parquet', index=False)
    if matches_df is not None:
        logging.info(f"Matches for profile {profile_name}:\n{matches_df}")
    else:
        logging.error(f"Failed to find matches for profile {profile_name}")

if __name__ == "__main__":
    main()
