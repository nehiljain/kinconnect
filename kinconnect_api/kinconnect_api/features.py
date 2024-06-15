from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_fireworks import ChatFireworks
from langchain_fireworks import FireworksEmbeddings
from kinconnect_api.config import MONGO_CONNECTION_STRING, RAW_DATA_DIR, load_dotenv
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from textwrap import dedent

import pandas as pd
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Callable, Union

load_dotenv()

class CareerEntry(BaseModel):
    company: str = Field(..., title="Company they worked at")
    title: str = Field(..., title="Title of the role they held")
    description: str = Field(..., title="Description of the role they held")
    start_date: str = Field(..., title="Start date of the role")
    end_date: str = Field(..., title="End date of the role")


class ProjectEntry(BaseModel):
    title: str = Field(..., title="Title of the project")
    description: str = Field(..., title="Description of the project")


class ProfileModel(BaseModel):
    name: str = Field(..., title="Name of the person")
    honors: list[str] = Field(None, title="Honors, Awards and recognition they have received in life")
    interests: list[str] = Field(..., title="Interests and current focus of theirs the work or the event")
    skills: list[str] = Field(..., title="Skills they have")
    career: List[CareerEntry] = Field(..., title="Career history of the person")
    past_projects: List[ProjectEntry] = Field(..., title="Projects they have worked on")
    elevator_pitch: str = Field(..., title="Elevator pitch for the person for the event")



class QAPair(BaseModel):
    question: str = Field(..., title="Question")
    answer: str = Field(..., title="Answer")

class FormSubmission(BaseModel):
    qa_pairs: List[QAPair] = Field(..., title="QA pairs")


def get_career(profile):
    prompt_str = dedent("""
You are a data generation app which creates profiles for participants at a hackathon. 
Given their form submission which asks them a few questions. Create a profile. 
Find all the relevant details about their career.

<form_submission>                                   
{submission}
</form_submission>
""")
    mixtral_llm = ChatFireworks(
        model="accounts/fireworks/models/mistral-7b-instruct-v3")

    career_llm = mixtral_llm.with_structured_output(CareerEntry)

    prompt = ChatPromptTemplate.from_template(prompt_str)
    chain = prompt | career_llm
    return chain.invoke({"submission": profile})


def get_profile_details(profile):
    prompt_str = dedent("""
You are a data generation app which creates profiles for participants at a hackathon. 
Given their form submission which asks them a few questions. Create a profile. 
Find all the relevant details about their profile. Find their skills, accolades, honors and current interests.
Generate a name for the person. Make the name diverse and real representation of people working in the silicon valley with the relevant description of their form submission.
                        
<form_submission>                                   
{submission}
</form_submission>
""")
    # Define a Pydantic model for the profile
    class ProfileDetails(BaseModel):
        honors: List[str] = Field(None, title="Honors, Awards and recognition they have received in life")
        interests: List[str] = Field(..., title="Interests and current focus of theirs the work or the event")
        skills: List[str] = Field(..., title="Skills they have")
        name: str = Field(..., title="Name of the person")
        elevator_pitch: str = Field(..., title="Elevator pitch for the person for the event")
        
    gpt35_llm =  ChatOpenAI(model="gpt-3.5-turbo")

    career_llm = gpt35_llm.with_structured_output(ProfileDetails)

    prompt = ChatPromptTemplate.from_template(prompt_str)
    chain = prompt | career_llm
    return chain.invoke({"submission": profile})


def get_project(profile):
    prompt_str = dedent("""
You are a data generation app which creates profiles for participants at a hackathon. 
Given their form submission which asks them a few questions. Create a profile. 
Find all the relevant details about their past projects and portfolio.

<form_submission>                                   
{submission}
</form_submission>
""")
    mixtral_llm = ChatFireworks(
        model="accounts/fireworks/models/mistral-7b-instruct-v3")

    career_llm = mixtral_llm.with_structured_output(ProjectEntry)

    prompt = ChatPromptTemplate.from_template(prompt_str)
    chain = prompt | career_llm
    return chain.invoke({"submission": profile})


def get_full_profile(form_submission):
    
    
    founder_profile = f'\n\n'.join(f"## {pair.question}: \n {pair.answer}" for pair in form_submission)
    career = get_career(founder_profile)
    project = get_project(founder_profile)
    profile_details = get_profile_details(founder_profile)
    profile = ProfileModel(
            name=profile_details.name,
            honors=profile_details.honors,
            interests=profile_details.interests,
            skills=profile_details.skills,
            career=[
                CareerEntry(
                    company=career.company,
                    title=career.title,
                    description=career.description,
                    start_date=career.start_date,
                    end_date=career.end_date
                )
            ],
            past_projects=[
                ProjectEntry(
                    title=project.title,
                    description=project.description
                )
            ],
            elevator_pitch=profile_details.elevator_pitch
        )
    return profile

def get_profile_doc(profile: dict):
    past_projects_str = '\n'.join(get_project(item) for item in profile['past_projects'])
    
    career_str = '\n'.join(get_career(item) for item in profile['career'])

    prodile_doc = dedent(f'''

    This is the profile of {profile['name']}

    # Elevator Pitch of the person
    {profile['elevator_pitch']}

    # Career History and work experience of the person
    {career_str}

    # Past Projects and Portfolio
    {past_projects_str}

    # Skillset they have which will be useful for them
    {profile['skills']}

    # Their current focus and interests to match with relevant people
    {profile['interests']}


    # Awards and Honors they have won over their life
    {profile['honors']}
    ''')
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(prodile_doc)
    vector_search_index = "embedding_idx"
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents = md_header_splits,
        embedding = FireworksEmbeddings(model="nomic-ai/nomic-embed-text-v1.5"),
        collection = profiles_collection,
        index_name = vector_search_index
    )
    return vector_search