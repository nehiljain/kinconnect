from kinconnect_api.config import load_dotenv
from typing import List
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_fireworks import ChatFireworks
load_dotenv()

class ProjectEntry(BaseModel):
    title: str = Field(..., title="Title of the project")
    description: str = Field(..., title="Description of the project")

class Portfolio(BaseModel):
    projects: List[ProjectEntry] = Field(..., description="All the projects you have worked on")

def call_api(prompt, options, context):
    config = options.get('config', None)
    fireworks_llm = ChatFireworks(model=config['model'])
    fireworks_llm = fireworks_llm.with_structured_output(Portfolio)
    
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