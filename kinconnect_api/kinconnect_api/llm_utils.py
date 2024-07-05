import os
import logging
from kinconnect_api.config import load_dotenv
from typing import Any, Optional, Dict
from langchain_fireworks import ChatFireworks
from langchain_core.messages import HumanMessage

load_dotenv()

FIREFUNC_MODEL: str = "accounts/fireworks/models/firefunction-v2"
MISTRAL_MODEL: str = "accounts/fireworks/models/mistral-7b-instruct-v3"
LLAMA_70B_MODEL: str = 'accounts/fireworks/models/llama-v3-70b-instruct'

def call_fireworks_api_no_structure(prompt: str, model: str, api_key: str = None) -> Dict[str, Optional[Any]]:
    """
    Calls the API with the given prompt and model.

    Args:
        prompt (str): The prompt to send to the API.
        model (str): The model to use for the API call.
        api_key (str): The API key to use for authentication.

    Returns:
        Dict[str, Optional[Any]]: The output from the API call or an error message.
    """
    if api_key is None:
        api_key = os.getenv('FIREWORKS_API_KEY')
    fireworks_llm = ChatFireworks(model=model, api_key=api_key)
    try:
        output = fireworks_llm.invoke([HumanMessage(content=prompt)])
        return {
            "output": output.content,
            "error": None
        }
    except Exception as e:
        logging.error(f"API call failed: {e}")
        return {
            "output": None,
            "error": e
        }


def call_fireworks_api_with_structure(prompt: str, structured_class: Any, model: str, api_key: str = None) -> Dict[str, Any]:
    """Calls the Fireworks API with a structured output.

    Args:
        prompt (str): The prompt to send to the API.
        structured_class (Any): The structured class to use for the output.
        model (str): The model to use for the API call.
        api_key (str): The API key to use for authentication.

    Returns:
        Dict[str, Any]: The output from the API call.
    """
    if api_key is None:
        api_key = os.getenv('FIREWORKS_API_KEY')
    fireworks_llm = ChatFireworks(model=model, api_key=api_key).with_structured_output(structured_class)
    try:
        output = fireworks_llm.invoke([HumanMessage(content=prompt)])
        return {"output": output.dict(), "error": None}
    except Exception as e:
        logging.error(f"Error calling API: {e}")
        return {"output": None, "error": e}