import os
import json
import pickle
from datetime import datetime
import logging
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_fireworks import ChatFireworks
from kinconnect_api.config import load_dotenv, PROCESSED_DATA_DIR
from tqdm import tqdm
import requests
import pandas as pd
from thefuzz import process
import random
from pathlib import Path
from kinconnect_api.llm_utils import call_fireworks_api_with_structure, FIREFUNC_MODEL, MISTRAL_MODEL

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SYNTHETIC_DATA_PROMPT: str = '''
Generate a new profile by answering the questions. The form is a set of questions that a person (fictitious profile) answers before going to a hackathon. The profile is a complex data object. Use the examples below as inspiration for the type of answers. Each example is a concatenated string of question and answer in markdown format.

The goal is to create a good representation of a participant in the hackathon in Silicon Valley, US.

<form_questions>
1. **What is your name?** 
2. **What are your interests?  (ie technical topic, coding language, business problem).**
3. **If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.**
4. **If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.**
5. **What is your strongest functional role (such as developer, UX, business, product)? Please share one or two things about your experience in role your experience, for example a success, companies you worked for, how many years experience, a challenging project, etc.**
6. **Describe your career history? Think of it like a snapshot of your LinkedIn that is relevant for your teammates at this hackathon.**
7. **What are some of the projects you are proud of? Share links and description of what you did and why you are so proud of them**
8. **Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?**
</form_questions>

<examples>
1. "## What is your name? : \n Chloe Wong\n\n## What are your interests?  (ie technical topic, coding language, business problem).: \n I'm interested in Rags and AI LLMs\n\n## If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.: \n nan\n\n## What is your strongest functional role (such as developer, UX, business, product)? Please share one or two things about your experience in role your experience, for example a success, companies you worked for, how many years experience, a challenging project, etc.: \n Back end developer, 10 years, build and deployed backend databases for Netflix including adding AI functionality to Netflix recommendation engines. \n\n## Career path from Linkedin: \n Senior Software EngineerSenior Software Engineer, Netflix, Netflix , Jun 2018 - Present · 6 yrs 1 mo, PayPal 3 yrs 11 mos3 yrs 11 mos\n\n## Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?: \n Product, frontend, \n\n## Past Projects Portfolio: \n ### Project 1: **Netflix Recommendation Engine Enhancement**\n\n**Title:** AI-Powered Recommendation Engine for Netflix\n\n**Description:** Led the development and deployment of an advanced recommendation engine for Netflix. This project aimed to enhance the accuracy and personalization of content recommendations for users by integrating machine learning algorithms. The system utilized user behavior data, viewing history, and ratings to predict and suggest content that matched user preferences. The project included a real-time processing pipeline to ensure recommendations were updated dynamically as user interactions occurred.\n\n**Skills:** \n- Python\n- Machine Learning\n- TensorFlow/PyTorch\n- Apache Spark\n- AWS (S3, EC2, Lambda)\n- SQL\n- Big Data (Hadoop)\n- Data Engineering\n- API Development\n- Docker/Kubernetes\n\n### Project 2: **PayPal Fraud Detection System**\n\n**Title:** Real-Time Fraud Detection System for PayPal\n\n**Description:** Developed and deployed a robust fraud detection system for PayPal. This project involved creating a machine learning-based system to detect and prevent fraudulent transactions in real-time. The system analyzed transaction patterns, user behavior, and historical fraud data to identify suspicious activities. By implementing advanced algorithms and a scalable architecture, the system significantly reduced the incidence of fraud and enhanced the security of PayPal’s platform.\n\n**Skills:** \n- Java\n- Python\n- Machine Learning\n- Apache Kafka\n- NoSQL Databases (MongoDB, Cassandra)\n- SQL\n- Data Engineering\n- Real-Time Processing\n- Microservices Architecture\n- AWS (S3, EC2, Lambda)\n- Docker/Kubernetes\n\n### Project 3: **Netflix Data Lake**\n\n**Title:** Scalable Data Lake Infrastructure for Netflix\n\n**Description:** Designed and implemented a scalable data lake infrastructure for Netflix to store and manage vast amounts of data efficiently. The project involved setting up a distributed data storage system that could handle petabytes of structured and unstructured data. The data lake facilitated efficient data ingestion, storage, processing, and retrieval for various analytics and machine learning applications. This infrastructure played a crucial role in enabling data-driven decision-making across Netflix.\n\n**Skills:** \n- Java\n- Python\n- Apache Hadoop\n- Apache Spark\n- AWS (S3, EMR)\n- SQL\n- Data Engineering\n- ETL Processes\n- Distributed Systems\n- Docker/Kubernetes"

2. "## What is your name? : \n Rehka Mehta\n\n## What are your interests?  (ie technical topic, coding language, business problem).: \n Fashion \n\n## If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.: \n E-commerce\n\n## What is your strongest functional role (such as developer, UX, business, product)? Please share one or two things about your experience in role your experience, for example a success, companies you worked for, how many years experience, a challenging project, etc.: \n Product manager.  I am an expert in personal recommendation.\n\n## Career path from Linkedin: \n As a product manager at Wayfair, they lead the development of innovative e-commerce solutions to enhance customer experience. With expertise in data-driven decision-making, they drive projects that optimize the online shopping journey.\n\n## Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?: \n Data engineer\n\n## Past Projects Portfolio: \n ### Project 1: **Personalized Recommendation Engine for Wayfair**\n\n**Title:** Personalized Recommendation Engine for Wayfair\n\n**Description:** Led the development of a personalized recommendation engine for Wayfair's e-commerce platform. The project focused on leveraging customer data and advanced machine learning algorithms to provide tailored product recommendations. By analyzing user behavior, preferences, and purchase history, the engine delivered highly relevant suggestions, significantly increasing customer engagement and sales.\n\n**Skills:** \n- Machine Learning\n- Data Analysis\n- Product Management\n- Personalization\n\n### Project 2: **Enhanced Product Search and Discovery**\n\n**Title:** Enhanced Product Search and Discovery for Wayfair\n\n**Description:** Spearheaded the enhancement of Wayfair's product search and discovery features to improve the online shopping experience. The project involved optimizing search algorithms, implementing advanced filtering options, and integrating visual search capabilities. These improvements allowed customers to find products more easily and accurately, resulting in higher conversion rates and customer satisfaction.\n\n**Skills:** \n- Search Engine Optimization (SEO)\n- Data-Driven Decision Making\n- User Experience (UX) Design\n- Product Management\n\n### Project 3: **Customer Insights and Analytics Platform**\n\n**Title:** Customer Insights and Analytics Platform for Wayfair\n\n**Description:** Developed a comprehensive customer insights and analytics platform to support data-driven decision-making across Wayfair. The platform aggregated and analyzed customer data, providing actionable insights to inform marketing strategies, product development, and personalized customer experiences. This project enabled the company to better understand customer needs and preferences, driving more effective and targeted initiatives.\n\n**Skills:** \n- Data Analytics\n- Business Intelligence\n- Product Management\n- Customer Experience"
</examples>

Generate a new example with profile attributes of {profile_attr}. Generate the profile as a markdown string of question-answer pairs. 

Consider this while creating the profile answers:
1. Create profile with attributes: {profile_attr}
2. Foundational Roles should be mix bag of product managers, engineers, managers, investors across various profiles
3. For engineers, choose from a variety of profiles like startup founding engineers, data scientists, data engineers, platform engineers, frontend engineers, designers, UX, etc.
4. For project ideas for hackathon, the idea should be small. The core fundamental of the project related to generative AI, LLMs, diffusion models or applications of AI
5. For meeting people, it should align with other profiles of participants in the hackathon.
6. The career should be made up of real companies that exist in the world. Use innovative famous companies from variety of sectors. Feel free to choose companies from Y combinator and a16z portfolio. Format it like Title, Company Name, Description of their work, Start Date - End Date.
7. Project portfolio can have projects related classical machine learning (regression and classification), blockchain, e-commerce, recsys, search, web, mobile, ar, vr etc
'''

# Load prompt strings
PORTFOLIO_PROMPT_STRING: str = open("/Users/nehiljain/code/kinconnect/kinconnect_api/prompts/prompt_extract_portfolio.txt", "r").read()
PROFILE_PROMPT_STRING: str = open("/Users/nehiljain/code/kinconnect/kinconnect_api/prompts/prompt_extract_proile_attributes.txt", "r").read()
CAREER_HISTORY_PROMPT_STRING: str = open("/Users/nehiljain/code/kinconnect/kinconnect_api/prompts/prompt_extract_career_firefunc.txt", "r").read()

class ProfileModel(BaseModel):
    """Model representing a profile."""
    name: str = Field(..., title="Name of the person")
    honors: List[str] = Field(None, title="Honors, Awards and recognition they have received in life")
    interests: List[str] = Field(..., title="Interests and current focus of theirs the work or the event")
    skills: List[str] = Field(..., title="Skills they have")

class CareerEntry(BaseModel):
    """Model representing a career entry."""
    company: str = Field(..., description="Company they worked at")
    title: str = Field(..., description="Title of the role they held")
    description: str = Field(..., description="Description of the role they held")
    start_date: str = Field(..., description="Start date of the role")
    end_date: str = Field(..., description="End date of the role")

class CareerHistory(BaseModel):
    """Model representing career history."""
    history: List[CareerEntry] = Field(..., description="All the companies you have been at as part of your career")

class ProjectEntry(BaseModel):
    """Model representing a project entry."""
    title: str = Field(..., title="Title of the project")
    description: str = Field(..., title="Description of the project")

class Portfolio(BaseModel):
    """Model representing a portfolio."""
    projects: List[ProjectEntry] = Field(..., description="All the projects you have worked on")

class QuestionAnswer(BaseModel):
    """Model representing a question and answer pair."""
    question: str = Field(..., title="Question asked by the user")
    answer: str = Field(..., title="Answer given by the user")

class FormSubmission(BaseModel):
    """Model representing a form submission."""
    questions: List[QuestionAnswer] = Field(..., description="All the questions and answers of a profile")

class Names(BaseModel):
    """Model representing a list of names."""
    names: List[str] = Field(..., title="Names of hackathon participants in Silicon Valley. In 2024. It should have diversity of gender, race, ethnicity in the software engineering world.")



def generate_synthetic_form_submission_ai(profile_attr: str) -> Dict[str, Any]:
    """Generates a synthetic form submission using AI.

    Returns:
        Dict[str, Any]: The synthetic form submission.
    """
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": "accounts/fireworks/models/mixtral-8x22b-instruct",
        "max_tokens": 8192,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [{"role": "user", "content": SYNTHETIC_DATA_PROMPT.format(profile_attr=profile_attr)}]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('FIREWORKS_API_KEY')}"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def convert_question_answer_pair_to_markdown(question_answer_pair: Dict[str, str]) -> str:
    """Converts a question-answer pair to markdown format.

    Args:
        question_answer_pair (Dict[str, str]): The question-answer pair.

    Returns:
        str: The markdown formatted string.
    """
    return "\n\n".join([f"## {question}\n{answer}" for question, answer in question_answer_pair.items()])

def extract_career_history(question_answer_pair_markdown: str) -> Dict[str, Any]:
    """Extracts career history from a markdown formatted question-answer pair.

    Args:
        question_answer_pair_markdown (str): The markdown formatted question-answer pair.

    Returns:
        Dict[str, Any]: The extracted career history.
    """
    career_history_prompt = CAREER_HISTORY_PROMPT_STRING.replace("{{bio}}", question_answer_pair_markdown)
    return call_fireworks_api_with_structure(career_history_prompt, CareerHistory, FIREFUNC_MODEL)

def extract_profile_details(question_answer_pair_markdown: str) -> Dict[str, Any]:
    """Extracts profile details from a markdown formatted question-answer pair.

    Args:
        question_answer_pair_markdown (str): The markdown formatted question-answer pair.

    Returns:
        Dict[str, Any]: The extracted profile details.
    """
    profile_prompt = PROFILE_PROMPT_STRING.replace("{{bio}}", question_answer_pair_markdown)
    return call_fireworks_api_with_structure(profile_prompt, ProfileModel, MISTRAL_MODEL)

def extract_portfolio(question_answer_pair_markdown: str) -> Dict[str, Any]:
    """Extracts portfolio from a markdown formatted question-answer pair.

    Args:
        question_answer_pair_markdown (str): The markdown formatted question-answer pair.

    Returns:
        Dict[str, Any]: The extracted portfolio.
    """
    portfolio_prompt = PORTFOLIO_PROMPT_STRING.replace("{{bio}}", question_answer_pair_markdown)
    return call_fireworks_api_with_structure(portfolio_prompt, Portfolio, MISTRAL_MODEL)

def generate_profile_from_question_answer_pair(question_answer_pair: Dict[str, str]) -> Dict[str, Any]:
    """Generates a profile from a question-answer pair.

    Args:
        question_answer_pair (Dict[str, str]): The question-answer pair.

    Returns:
        Dict[str, Any]: The generated profile.
    """
    markdown_profile = convert_question_answer_pair_to_markdown(question_answer_pair)
    career_history = extract_career_history(markdown_profile)
    profile_details = extract_profile_details(markdown_profile)
    portfolio = extract_portfolio(markdown_profile)
    profile = profile_details['output']
    profile['career_history'] = career_history['output']
    profile['portfolio'] = portfolio['output']
    profile['form_submission'] = markdown_profile
    return profile

def get_form_question(question: str) -> str:
    """Gets the best matching form question.

    Args:
        question (str): The question to match.

    Returns:
        str: The best matching form question.
    """
    ideal_qna_pair = {
        "Timestamp": "01/07/2024 12:42:44",
        "What is your name? ": "Nehil",
        "What are your interests? (ie technical topic, coding language, business problem).": "test",
        "If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.": "test",
        "What is your strongest functional role (such as developer, UX, business, product)? Please share one or two things about your experience in role your experience, for example a success, companies you worked for, how many years experience, a challenging project, etc.": "test",
        "Describe your career history? Think of it like a snapshot of your LinkedIn that is relevant for your teammates at this hackathon.": "test",
        "What are some of the projects you are proud of? Share links and description of what you did and why you are so proud of them": "test",
        "Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?": "test",
        "What your email? (we will send you matching profiles there)": "",
        "Email address": "jain.nehil@gmail.com"
    }
    ideal_questions = ideal_qna_pair.keys()
    best_match, _ = process.extractOne(question, ideal_questions)
    return best_match

def get_unique_names(num_names: int = 30) -> List[str]:
    """Gets a list of unique names.

    Args:
        num_names (int): The number of unique names to get. Defaults to 30.

    Returns:
        List[str]: The list of unique names.
    """
    unique_names: List[str] = []
    prompts: List[str] = [
        'Generate 15 full names for software engineers from diverse ethnic backgrounds, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 10 full names for Indian software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 12 full names for Chinese software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 15 full names for Korean software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 11 full names for Japanese software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 16 full names for African American software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 13 full names for White software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 19 common full names for software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 18 full names for Hispanic software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.',
        'Generate 10 full names for Middle Eastern software engineers, equal male and female. Provide only proper realistic names in the format: Firstname Lastname.'
    ]

    while len(unique_names) <= num_names:
        response = call_fireworks_api_with_structure(random.choice(prompts), Names, MISTRAL_MODEL)
        unique_names += list(set(response['output']['names']))
    logging.info(f"Generated {len(unique_names)} unique names - {unique_names}")
    return unique_names

def process_synthetic_data(synthetic_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Processes synthetic data.

    Args:
        synthetic_data (List[Dict[str, Any]]): The synthetic data to process.

    Returns:
        List[Dict[str, Any]]: The processed profiles.
    """
    processed_profiles: List[Dict[str, Any]] = []
    qna_pairs: List[Dict[str, str]] = [
        {get_form_question(item['question']): item['answer'] for item in data['questions']}
        for data in synthetic_data if data is not None
    ]
    for qna_pair in qna_pairs:
        logging.debug(f"Processing QnA Pair: {qna_pair}")
        profile = generate_profile_from_question_answer_pair(qna_pair)
        logging.info(f"Generated Profile: {profile}")
        processed_profiles.append(profile)
    return processed_profiles

def assign_unique_names(processed_profiles: List[Dict[str, Any]], unique_names: List[str]) -> None:
    """Assigns unique names to processed profiles. This is because AI generates the same names again and again.

    Args:
        processed_profiles (List[Dict[str, Any]]): The processed profiles.
        unique_names (List[str]): The list of unique names.
    """
    for profile in processed_profiles:
        logging.debug(f"Assigning unique name to profile: {profile}")
        if unique_names:
            original_name = profile['name']
            profile['name'] = unique_names.pop(random.randrange(len(unique_names)))
            profile['name'] += " (Fake Profile)"
            profile['form_submission'] = profile['form_submission'].replace(original_name, profile['name'])
        logging.info(f"Updated Profile with Unique Name: {profile}")
import argparse

def main(num: int, output_dir: str, profile_attr: str) -> None:
    """Main function to generate and process synthetic data."""
    synthetic_data: List[Dict[str, Any]] = []
    for _ in tqdm(range(num)):
        logging.debug(f'Generating synthetic data for profile attr: {profile_attr}')
        synth_form_submission = generate_synthetic_form_submission_ai(profile_attr)
        extract_synthetic_qna_prompt = f'''
            Separate the questions and answers into a structured format.

            {synth_form_submission['choices'][0]['message']['content']}
        '''
        qna_parsed = call_fireworks_api_with_structure(extract_synthetic_qna_prompt, FormSubmission, FIREFUNC_MODEL)
        synthetic_data.append(qna_parsed['output'])
    logging.info("Synthetic data generation complete.")
    
    processed_data_dir = Path(output_dir)
    processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    synthetic_data_path = processed_data_dir / f"synth_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.pkl"
    with open(synthetic_data_path, "wb") as f:
        pickle.dump(synthetic_data, f)
    logging.info(f"Synthetic {len(synthetic_data)} profiles saved to {synthetic_data_path}")

    processed_profiles = process_synthetic_data(synthetic_data)
    unique_names = get_unique_names(len(processed_profiles))
    assign_unique_names(processed_profiles, unique_names)
    
    processed_filename = processed_data_dir / f"processed_profiles_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(processed_filename.with_suffix(".pkl"), "wb") as f:
        pickle.dump(processed_profiles, f)
    logging.info(f"Processed {len(processed_profiles)} profiles saved to {processed_filename.with_suffix('.pkl')}")
    
    process_profiles_df = pd.DataFrame(processed_profiles)
    process_profiles_df.to_parquet(processed_filename.with_suffix(".parquet"), index=False)
    logging.info(f"Processed {len(processed_profiles)} profiles saved to {processed_filename.with_suffix('.parquet')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and process synthetic data.")
    parser.add_argument('--profile_attr', type=str, help='Attribute to give AI to generate profiles for')
    parser.add_argument('--num', type=int, default=2, help='Number of iterations for synthetic data generation')
    parser.add_argument('--output_dir', type=str, default=PROCESSED_DATA_DIR, help='Directory to save the processed data')
    args = parser.parse_args()
    logging.debug(f'args: {args}')
    
    main(num=args.num, output_dir=args.output_dir, profile_attr=args.profile_attr)
