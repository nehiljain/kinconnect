import pickle
import logging
from pathlib import Path
from pymongo import MongoClient, UpdateOne
from typing import List, Dict
from langchain_fireworks import FireworksEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from kinconnect_api.config import MONGO_CONNECTION_STRING, PROCESSED_DATA_DIR, load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_mongo_client() -> MongoClient:
    """Get a MongoDB client."""
    return MongoClient(MONGO_CONNECTION_STRING)

def get_synthetic_profiles_from_files(processed_data_dir: Path) -> List[Dict]:
    """Retrieve synthetic profiles from pickle files.

    Args:
        processed_data_dir (Path): Directory containing processed profile files.

    Returns:
        List[Dict]: List of synthetic profiles.
    """
    all_profiles: List[Dict] = [
        profile
        for file in processed_data_dir.glob("processed_profiles_*.pkl")
        for profile in pickle.load(open(file, "rb"))
    ]
    return all_profiles

def insert_new_profiles(profiles: List[Dict], collection) -> List[Dict]:
    """Insert new profiles into the MongoDB collection.

    Args:
        profiles (List[Dict]): List of profiles to insert.
        collection: MongoDB collection to insert profiles into.

    Returns:
        List[Dict]: List of newly inserted profiles.
    """
    existing_names: set = set(collection.distinct("name"))
    new_profiles: List[Dict] = [profile for profile in profiles if profile['name'] not in existing_names]
    
    if new_profiles:
        collection.insert_many(new_profiles)
        logging.info(f"Inserted {len(new_profiles)} new profiles")
    return new_profiles

def get_vector_store() -> MongoDBAtlasVectorSearch:
    return MongoDBAtlasVectorSearch.from_connection_string(
        connection_string = MONGO_CONNECTION_STRING,
        namespace = "kinconnect.profile_chunks",
        embedding = FireworksEmbeddings(model="nomic-ai/nomic-embed-text-v1.5"),
        index_name = "profile_chunks"
    )

def get_profile_by_name(name: str) -> Dict:
    client = get_mongo_client()
    db = client['kinconnect']
    profiles_collection = db['profiles']
    return profiles_collection.find_one({'name': name})

def get_profiles_to_chunk() -> List[Dict]:
    """Get profiles to chunk from the MongoDB collection.

    Returns:
        List[Dict]: List of profiles to chunk.
    """
    client = get_mongo_client()
    db = client['kinconnect']
    profiles_collection = db['profiles']
    profile_chunks_collection = db['profile_chunks']
    
    existing_profiles: set = set(profile_chunks_collection.distinct("name"))
    profiles_to_chunk: List[Dict] = [profile for profile in profiles_collection.find() if profile['name'] not in existing_profiles]
    return profiles_to_chunk

def update_profiles_with_fake_suffix(collection) -> None:
    """Update profiles in the MongoDB collection with a fake suffix.

    Args:
        collection: MongoDB collection to update profiles in.
    """
    profiles_to_update = collection.find({"name": {"$not": {"$regex": r"\(Fake Profile\)$"}}})
    updates: List[UpdateOne] = [
        UpdateOne({"_id": profile["_id"]}, {"$set": {"name": profile['name'] + " (Fake Profile)"}})
        for profile in profiles_to_update
    ]
    
    if updates:
        collection.bulk_write(updates)
        logging.info(f"Updated {len(updates)} profiles with (Fake Profile) suffix")

def delete_profile_and_chunks(profile_name: str) -> None:
    """
    Deletes a profile and its associated chunks from the database.

    Args:
        profile_name (str): The name of the profile to delete.
    """
    client = get_mongo_client()
    db = client['kinconnect']
    profiles_collection = db['profiles']
    profile_chunks_collection = db['profile_chunks']
    
    try:
        # Delete the profile
        profiles_collection.delete_many({'name': profile_name})
        logging.info(f"Deleted profile with name: {profile_name}")
        # Delete associated chunks
        profile_chunks_collection.delete_many({'name': profile_name})
        logging.info(f"Deleted chunks associated with profile name: {profile_name}")
    except Exception as e:
        logging.error(f"Error deleting profile and chunks: {e}")

def seed_db_with_synthetic_profiles() -> None:
    """Main function to process and update synthetic profiles."""
    processed_data_dir: Path = Path(PROCESSED_DATA_DIR)
    synthetic_profiles: List[Dict] = get_synthetic_profiles_from_files(processed_data_dir)
    client = get_mongo_client()
    db = client['kinconnect']
    profiles_collection = db['profiles']
    new_profiles: List[Dict] = insert_new_profiles(synthetic_profiles, profiles_collection)
    # this was one time thing to keep the data clean as the data evolved
    # update_profiles_with_fake_suffix(profiles_collection)

if __name__ == "__main__":
    seed_db_with_synthetic_profiles()