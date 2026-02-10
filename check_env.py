from dotenv import load_dotenv
import os

env_path = os.path.join(os.getcwd(), '.env')
print(f"Loading .env from: {env_path}")
loaded = load_dotenv(env_path)
print(f"load_dotenv returned: {loaded}")

key = os.getenv("OPENAI_API_KEY")
if key:
    print(f"OPENAI_API_KEY loaded: {key[:5]}...{key[-5:]}")
else:
    print("OPENAI_API_KEY NOT loaded")
