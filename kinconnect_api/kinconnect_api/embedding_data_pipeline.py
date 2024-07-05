import logging
from typing import List, Dict, Any
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.schema import Document
from langchain_fireworks import FireworksEmbeddings
from dotenv import load_dotenv
from kinconnect_api.db import get_profiles_to_chunk, PROFILE_CHUNKS_COLLECTION, get_vector_store

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

def get_chunks(profile: Dict[str, Any]) -> List[Document]:
    """Splits the profile's form submission into chunks and adds metadata.

    Args:
        profile (Dict[str, Any]): The profile containing form submission data.

    Returns:
        List[Document]: A list of Document objects with added metadata.
    """
    headers_to_split_on = [('##', "question")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    splits = markdown_splitter.split_text(profile['form_submission'])
    
    for split in splits:
        split.metadata['profile_id'] = str(profile['_id'])
        split.metadata['name'] = profile['name']
    
    return splits

def chunk_and_embed_profiles(profiles: List[Dict[str, Any]]) -> None:
    """Chunks and embeds profiles into the vector store.

    Args:
        profiles (List[Dict[str, Any]]): A list of profiles to be chunked and embedded.
    """
    all_chunks = [chunk for profile in profiles for chunk in get_chunks(profile)]
    vector_store = get_vector_store()
    vector_store.add_documents(all_chunks)
    logging.info(f"Added {len(all_chunks)} chunks to vector store")
    return all_chunks

def main() -> None:
    """Main function to chunk and embed profiles."""
    profiles = get_profiles_to_chunk()
    logging.info(f"Profiles to chunk are : {len(profiles)}")
    all_chunks = chunk_and_embed_profiles(profiles)
    logging.debug(f"All chunks: {all_chunks}")

if __name__ == "__main__":
    main()