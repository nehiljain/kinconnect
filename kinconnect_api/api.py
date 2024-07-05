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