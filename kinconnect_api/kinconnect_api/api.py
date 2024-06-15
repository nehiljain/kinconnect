from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_mongodb import MongoDBAtlasVectorSearch
from typing import List
from pymongo import MongoClient
from langchain_fireworks import ChatFireworks
from kinconnect_api.config import MONGO_CONNECTION_STRING, RAW_DATA_DIR, load_dotenv
from kinconnect_api.features import get_full_profile
import pandas as pd
import pandas as pd
from typing import List, Dict, Callable, Union
import os
from fastapi.middleware.cors import CORSMiddleware

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



# # @app.get("/profiles/{name}", response_model=ProfileModel)
# # def read_profile(name: str):
# #     profile = profiles_collection.find_one({"name": name})
# #     if profile is None:
# #         raise HTTPException(status_code=404, detail="Profile not found")
# #     return ProfileModel(**profile)

@app.put("/profiles/", response_model=ProfileModel)
def update_profile(profile: ProfileModel):
    updated_profile = profiles_collection.find_one_and_update(
        {"name": profile.name},
        {"$set": profile.model_dump()},
        return_document=True
    )
    print(f"updated_profile: {updated_profile}")
    # if updated_profile is None:
    #     raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileModel(**updated_profile)


# # if __name__ == "__main__":
# #     app.deploy("api")

# # from fastapi import FastAPI

# # app = FastAPI()


