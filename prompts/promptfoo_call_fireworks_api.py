from kinconnect_api.config import load_dotenv
from typing import List
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_fireworks import ChatFireworks
load_dotenv()

class CareerEntry(BaseModel):
    company: str = Field(..., description="Company they worked at")
    title: str = Field(..., description="Title of the role they held")
    description: str = Field(..., description="Description of the role they held")
    start_date: str = Field(..., description="Start date of the role")
    end_date: str = Field(..., description="End date of the role")

class CareerHistory(BaseModel):
    history: List[CareerEntry] = Field(..., description="All the companies you have been at as part of your career")

def call_api(prompt, options, context):
    config = options.get('config', None)
    fireworks_llm = ChatFireworks(model=config['model'])
    fireworks_llm = fireworks_llm.with_structured_output(CareerHistory)
    
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