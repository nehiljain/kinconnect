from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_fireworks import FireworksEmbeddings
from typing import List
from pymongo import MongoClient
from langchain_fireworks import ChatFireworks
from kinconnect_api.config import MONGO_CONNECTION_STRING, RAW_DATA_DIR, load_dotenv
from kinconnect_api.features import get_full_profile
import pandas as pd
import pandas as pd
from typing import List, Dict, Callable, Union
from fastapi.middleware.cors import CORSMiddleware
from kinconnect_api.search.search import Search
import kinconnect_api.util.collections

load_dotenv()
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

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


# Connect to MongoDB
def get_db():
    client = MongoClient(MONGO_CONNECTION_STRING)
    return client['kinconnect']

db = get_db()
profiles_collection = db['demo_profiles']

class QAPair(BaseModel):
    question: str = Field(..., title="Question")
    answer: str = Field(..., title="Answer")



@app.post("/profiles/", response_model=ProfileModel)
def create_profile(form_submission: List[QAPair]):
    print(form_submission)
    profile =  get_full_profile(form_submission)
    if profiles_collection.find_one({"name": profile.name}):
        raise HTTPException(status_code=4000, detail="Profile with this name already exists")
    # profiles_collection.insert_one(profile.model_dump())
    return profile


@app.put("/profiles/", response_model=ProfileModel)
def update_profile(profile: ProfileModel):
    # Define the filter and update
    new_values = {"$set": profile.model_dump()}

    # Update the document
    result = profiles_collection.update_one({"name": profile.name}, new_values)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile



@app.get("/search/", response_model=List[ProfileModel])
def search(profile: ProfileModel):
    profiles = perform_similarity_search(profile.elevator_pitch)
    return profiles

def create_vector_search():
        """
        Creates a MongoDBAtlasVectorSearch object using the connection string, database, and collection names, along with the OpenAI embeddings and index configuration.

        :return: MongoDBAtlasVectorSearch object
        """
        vector_search = MongoDBAtlasVectorSearch.from_connection_string(
            MONGO_CONNECTION_STRING,
            "kinconnect.demo_profiles",
            FireworksEmbeddings(model="nomic-ai/nomic-embed-text-v1.5"),
            index_name="default"
        )
        return vector_search


def perform_similarity_search(query, top_k=3):
    """
    This function performs a similarity search within a MongoDB Atlas collection. It leverages the capabilities of the MongoDB Atlas Search, which under the hood, may use the `$vectorSearch` operator, to find and return the top `k` documents that match the provided query semantically.

    :param query: The search query string.
    :param top_k: Number of top matches to return.
    :return: A list of the top `k` matching documents with their similarity scores.
    """

    # Get the MongoDBAtlasVectorSearch object
    vector_search = create_vector_search()

    # Execute the similarity search with the given query
    results = vector_search.similarity_search_with_score(
        query=query,
        k=top_k,
    )
    if updated_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileModel(**updated_profile)

@app.put("/search", response_model=ProfileModel)
def search(name: str, profiles: list[ProfileModel]):
    profile = db.profiles.find_one(
        {"name": name},
        return_document=True
    )
    profile = ProfileModel(**profile)
    simplified_profile = ProfileModel()
    simplified_profile.elevator_pitch = profile.elevator_pitch
    simplified_profile.interests = profile.interests
    query =kinconnect_api.util.collections.get_profile_doc(profile)

    handler = Search()
    profiles = handler.perform_similarity_search(query)
    return profiles

