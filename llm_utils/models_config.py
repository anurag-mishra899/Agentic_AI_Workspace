import os 
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv(r'/Users/anuragmishra/Documents/AI Workspace/env_vars/.env')

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT')        
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15')
OPENAI_API_TYPE = os.getenv('OPENAI_API_TYPE', 'azure')


openai_llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,  # or your deployment
    api_version=AZURE_OPENAI_API_VERSION,  # or your api version
    temperature=0,
    max_tokens=None,
    timeout=100,
    max_retries=2,
    # other params...
)