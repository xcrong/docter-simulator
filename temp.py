import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")


print(openai.api_key, openai.api_base)