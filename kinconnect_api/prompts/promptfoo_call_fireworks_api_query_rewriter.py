from kinconnect_api.config import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_fireworks import ChatFireworks
load_dotenv()


def call_api(prompt, options, context):
    config = options.get('config', None)
    fireworks_llm = ChatFireworks(model=config['model'])
    
    try:
        output = fireworks_llm.invoke([HumanMessage(content=prompt)])
        return {
            "output": output,
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