from kinconnect_api.config import MONGO_CONNECTION_STRING
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_fireworks import FireworksEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from textwrap import dedent

def get_project(item):
    return dedent(f'''
        Title: {item['title']}
        Description: {item['description']}
        ''')

def get_career(item):
    return dedent(f'''
        Company Name: {item['company']}
        Title: {item['title']}
        Description: {item['description']}
        Start Date: {item['start_date']}
        End Date: {item['end_date']}
        ''')

def get_profile_doc(profile: dict):
    if 'past_projects' in profile and len(profile['past_projects']) > 0:
        past_projects_str = '\n'.join(get_project(item) for item in profile['past_projects'])
    else:
        past_projects_str = ""
    if 'career' in profile and len(profile['career']) > 0:
        career_str = '\n'.join(get_career(item) for item in profile['career'])
    else:
        career_str = ""

    profile_doc = dedent(f'''

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


    return profile_doc

