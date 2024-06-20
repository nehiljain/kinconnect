from kinconnect_api.config import load_dotenv
from typing import List
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_fireworks import ChatFireworks
load_dotenv()

class ProfileModel(BaseModel):
    name: str = Field(..., title="Name of the person")
    honors: list[str] = Field(None, title="Honors, Awards and recognition they have received in life")
    interests: list[str] = Field(..., title="Interests and current focus of theirs the work or the event")
    skills: list[str] = Field(..., title="Skills they have")


def call_api(prompt, options, context):
    config = options.get('config', None)
    fireworks_llm = ChatFireworks(model=config['model'])
    fireworks_llm = fireworks_llm.with_structured_output(ProfileModel)
    
    try:
        output = fireworks_llm.invoke([HumanMessage(content=prompt)])
        return {
            "output": output.dict(),
            "error": None
        }
    except Exception as e:
        return {
            "output": None,
            "error": e
        }

if __name__ == "__main__":
    # just smoke test if the code works
    print(call_api("I am a google engineer with 2 years of experience", {'config': {'model': 'accounts/fireworks/models/mistral-7b-instruct-v3'}}, {}))