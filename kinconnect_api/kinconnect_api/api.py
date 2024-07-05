from typing import Dict
from modal import App, web_endpoint, Image, Secret
import logging
import re
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage
from langchain_fireworks import ChatFireworks
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
import os
from langchain_fireworks import ChatFireworks
from langchain_core.messages import HumanMessage
from pymongo import MongoClient
from typing import List, Dict
from langchain_fireworks import FireworksEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from kinconnect_api.match import get_matches_for_profile_with_name  # Changed to absolute import

logging.basicConfig(level=logging.INFO)

datascience_image = (
    Image.debian_slim(python_version="3.11")
    .pip_install(
        "pydantic==2.7.3",
        "thefuzz==0.22.1",
        "pandas==2.2.2",
        "requests==2.32.3",
        "langserve==0.2.1",
        "langchain[all]==0.2.5",
        "langchain-core==0.2.10",
        "langchain-community==0.2.5",
        "python-dotenv==1.0.1",
        "loguru==0.7.2",
        "langchain-mongodb==0.1.6",
        "pymongo==4.7.3",
        "langchain-fireworks==0.1.3",
        "modal==0.62.223",
        "langchain-text-splitters==0.2.2",
        "motor==3.5.0"
    )
)
app = App("kinconnect-api")



# # def get_vector_store() -> MongoDBAtlasVectorSearch:
# #     return MongoDBAtlasVectorSearch.from_connection_string(
# #         connection_string = os.getenv('MONGO_CONNECTION_STRING'),
# #         namespace = "kinconnect.profile_chunks",
# #         embedding = FireworksEmbeddings(model="nomic-ai/nomic-embed-text-v1.5"),
# #         index_name = "profile_chunks"
# #     )

# # def get_profile_by_name(name: str) -> Dict:
# #     client = MongoClient(os.getenv('MONGO_CONNECTION_STRING'))
# #     DB = client['kinconnect']
# #     PROFILES_COLLECTION = DB['profiles']
# #     return PROFILES_COLLECTION.find_one({'name': name})


# # def call_fireworks_api_no_structure(prompt: str, model: str) -> Dict[str, Optional[Any]]:
# #     """
# #     Calls the API with the given prompt and model.

# #     Args:
# #         prompt (str): The prompt to send to the API.
# #         model (str): The model to use for the API call.

# #     Returns:
# #         Dict[str, Optional[Any]]: The output from the API call or an error message.
# #     """
# #     fireworks_llm = ChatFireworks(model=model)
# #     try:
# #         output = fireworks_llm.invoke([HumanMessage(content=prompt)])
# #         return {
# #             "output": output.content,
# #             "error": None
# #         }
# #     except Exception as e:
# #         print(f"API call failed: {e}")
# #         return {
# #             "output": None,
# #             "error": e
# #         }


# # def call_fireworks_api_with_structure(prompt: str, structured_class: Any, model: str) -> Dict[str, Any]:
# #     """Calls the Fireworks API with a structured output.

# #     Args:
# #         prompt (str): The prompt to send to the API.
# #         structured_class (Any): The structured class to use for the output.
# #         model (str): The model to use for the API call.

# #     Returns:
# #         Dict[str, Any]: The output from the API call.
# #     """
# #     fireworks_llm = ChatFireworks(model=model).with_structured_output(structured_class)
# #     try:
# #         output = fireworks_llm.invoke([HumanMessage(content=prompt)])
# #         return {"output": output.dict(), "error": None}
# #     except Exception as e:
# #         print(f"Error calling API: {e}")
# #         return {"output": None, "error": e}

# # QUERY_PROMPT: str = """I have a request to match with a database of engineers, designers, project managers etc. This request in the form of answers to two questions. 

# # Each profile in database includes their skills, projects, career history, and interests. 
# # The goal is to expand this request into one cohesive ask to ensure it captures all relevant aspects and nuances needed for accurate matching. 

# # Here is the request in question answer pairs:

# # # Query Context
# # "{context}"

# # Please expand this request to include additional relevant details, such as specific skills, roles, project types, and any other contextual information that would improve the accuracy of matching with the profiles in the database. Consider what someone might need in a hackathon context, including complementary skills, leadership qualities, and relevant experience. This request will be used to do semantic search on the database. So the description and content of the request is very very crucial for accuracy.

# # Respond in <expanded_request> xml tags. The request should have all the answers and details. No yapping. No other text."""

# # REWRITE_SUMMARY_QUERY: str = '''
# # Understand the request and rewrite it in a easy to understand manner. Make sure to capture all the details. Write in 2 paragraphs like a formal and professional tone. Describe technologies, skills and details in specific details.

# # Request: {context}
# # '''


# # def extract_answer_from_submission(question: str, form_submission: str) -> Optional[Dict[str, str]]:
# #     """
# #     Extracts the answer to a specific question from the form submission.

# #     Args:
# #         question (str): The question to search for in the form submission.
# #         form_submission (str): The form submission text.

# #     Returns:
# #         Optional[Dict[str, str]]: A dictionary containing the question and its answer, or None if not found.
# #     """
# #     pattern = re.compile(rf"{re.escape(question)}\n(.*?)\n##", re.DOTALL)
# #     match = pattern.search(form_submission)

# #     if match:
# #         answer = match.group(1)
# #         return {
# #             "question": question,
# #             "answer": answer
# #         }
# #     else:
# #         return None

# # def create_profile_matching_request(profile: Dict[str, Any]) -> Optional[str]:
# #     """
# #     Creates a profile matching request based on the given profile.

# #     Args:
# #         profile (Dict[str, Any]): The profile containing form submission data.

# #     Returns:
# #         Optional[str]: The expanded query string or None if an error occurred.
# #     """
# #     form_submission: str = profile['form_submission']
# #     people_to_meet: Optional[Dict[str, str]] = extract_answer_from_submission(
# #         question="## Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?",
# #         form_submission=form_submission
# #     )
# #     project_idea: Optional[Dict[str, str]] = extract_answer_from_submission(
# #         question="## If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.",
# #         form_submission=form_submission
# #     )

# #     if not people_to_meet or not project_idea:
# #         print("Failed to extract necessary information from form submission.")
# #         return None

# #     context: str = f"""Topic: {people_to_meet['question']}
# #         Request: {people_to_meet['answer']}

# #         Topic: {project_idea['question']}
# #         Request: {project_idea['answer']}"""
    
# #     expanded_request: Optional[str] = generate_expanded_request(context)
# #     if expanded_request is None:
# #         return None

# #     expanded_query_string: Optional[str] = summarize_expanded_request(expanded_request)
# #     return expanded_query_string

# # def generate_expanded_request(context: str) -> Optional[str]:
# #     """
# #     Generates an expanded request using the given context.

# #     Args:
# #         context (str): The context to use for generating the expanded request.

# #     Returns:
# #         Optional[str]: The expanded request or None if an error occurred.
# #     """
# #     rewrite_query_prompt: str = QUERY_PROMPT.format(context=context)
# #     MISTRAL_MODEL: str = "accounts/fireworks/models/mistral-7b-instruct-v3"
# #     response: Dict[str, Optional[Any]] = call_fireworks_api_no_structure(rewrite_query_prompt, MISTRAL_MODEL)
# #     if response['error']:
# #         print("Failed to generate expanded request.")
# #         return None
# #     return response['output']

# # def summarize_expanded_request(expanded_request: str) -> Optional[str]:
# #     """
# #     Summarizes the expanded request.

# #     Args:
# #         expanded_request (str): The expanded request to summarize.

# #     Returns:
# #         Optional[str]: The summarized expanded request or None if an error occurred.
# #     """
# #     summary_prompt: str = REWRITE_SUMMARY_QUERY.format(context=expanded_request)
# #     LLAMA_70B_MODEL: str = 'accounts/fireworks/models/llama-v3-70b-instruct'
# #     response: Dict[str, Optional[Any]] = call_fireworks_api_no_structure(summary_prompt, LLAMA_70B_MODEL)
# #     if response['error']:
# #         return None
# #     return response['output']


# # def get_match_summary_explanation(expanded_request: str, profile: Dict[str, Any]) -> Optional[str]:
# #     """
# #     Get the summary explanation for a match.
# #     """
# #     summary_explain_prompt_template = '''
# #     You are given a detailed, expanded query and a matched profile of an engineer. Your task is to generate a summary explanation that highlights why the profile is a good match for the query. The summary should include key points about the engineer's skills, experiences, and projects that align with the needs and goals outlined in the query. Ensure that the explanation is clear, concise, and compelling, emphasizing the most relevant aspects of the match.

# #     Expanded Query:

# #     Copy code
# #     {expanded_query}
# #     Matched Profile:

# #     Copy code
# #     {matched_profile}

# #     Your response should be technical, consise and fun to read. It should be no more than 100 words. No yapping.
# #     Enclose your response in <summary> tags.
# #     '''
# #     summary_explain_prompt = summary_explain_prompt_template.format(expanded_query=expanded_request, matched_profile=profile['form_submission'])
# #     LLAMA_70B_MODEL: str = 'accounts/fireworks/models/llama-v3-70b-instruct'
# #     response: Dict[str, Optional[Any]] = call_fireworks_api_no_structure(summary_explain_prompt, LLAMA_70B_MODEL)
# #     class SummaryExplanation(BaseModel):
# #         summary: str = Field(description="The summary explanation for a matched profile to the request.")
# #     structure_parse_prompt = f'''
# #     You are given a response from an LLM. Your task is to parse the response and return the summary explanation.
# #     Response:
# #     {response}
# #     '''
# #     FIREFUNC_MODEL: str = "accounts/fireworks/models/firefunction-v2"
# #     summary_response = call_fireworks_api_with_structure(structure_parse_prompt, SummaryExplanation, FIREFUNC_MODEL)
# #     return summary_response['output']['summary']

# # def get_match_profiles(query_text: str, profile_collection) -> List[Dict[str, Any]]:
# #     """ 
# #     Retrieves matching profiles based on the query text.

# #     Args:
# #         query_text (str): The query text to search for matching profiles.

# #     Returns:
# #         List[Dict[str, Any]]: A list of matching profiles.
# #     """
# #     vector_store = get_vector_store()
# #     documents_with_scores = vector_store.similarity_search_with_score(query_text, k=5)
# #     profile_names = [doc.metadata['name'] for doc, score in documents_with_scores]
# #     profiles = list(profile_collection.find({'name': {'$in': profile_names}}))
# #     return profiles

# def get_matches_for_profile_with_name(name: str, profile_collection) -> Optional[pd.DataFrame]:
#     """
#     Retrieves matching profiles for a given profile name.

#     Args:
# #         name (str): The name of the profile to find matches for.

# #     Returns:
# #         Optional[pd.DataFrame]: A DataFrame containing the matching profiles or None if no matches found.
# #     """
#     profile = get_profile_by_name(name)
#     if not profile:
#         print(f"No profile found with name: {name}")
#         return None
#     query_string = create_profile_matching_request(profile)
#     if not query_string:
#         print("Failed to create profile matching request.")
#         return None
#     profile_matches = get_match_profiles(query_string, profile_collection)
#     profile_matches = [match for match in profile_matches if match.get('name') != name]
#     df = pd.DataFrame(profile_matches)
#     df['summary_explanation'] = df.apply(lambda row: get_match_summary_explanation(expanded_request=query_string, profile=row), axis=1)
#     df.drop(columns=['_id', 'form_submission'], inplace=True)
#     return df


@app.function(image=datascience_image, secrets=[Secret.from_name("kinconnect-secrets")])
@web_endpoint(method="POST")
def matches(data: Dict):
    name = data['name']
    logging.info(f"Getting matches for {name}")
    matches_df = get_matches_for_profile_with_name(name)
    if matches_df is not None:
        return matches_df.to_dict(orient='records')
    else:
        return None