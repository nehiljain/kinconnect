from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from kinconnect_api.search.search import Search
import kinconnect_api.util.collections

app = FastAPI()

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

client = MongoClient("mongodb://localhost:27017")
db = client.kinconnect

@app.post("/profiles/", response_model=ProfileModel)
def create_profile(profile: ProfileModel):
    if db.profiles.find_one({"name": profile.name}):
        raise HTTPException(status_code=400, detail="Profile with this name already exists")
    db.profiles.insert_one(profile.model_dump())
    return profile

@app.get("/profiles/{name}", response_model=ProfileModel)
def read_profile(name: str):
    profile = db.profiles.find_one({"name": name})
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileModel(**profile)

@app.put("/profiles/{name}", response_model=ProfileModel)
def update_profile(name: str, profile: ProfileModel):
    updated_profile = db.profiles.find_one_and_update(
        {"name": name},
        {"$set": profile.model_dump()},
        return_document=True
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