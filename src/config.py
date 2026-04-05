import os
from dotenv import load_dotenv

# Load environment variables from the .env file into the system environment
load_dotenv()

# Set constants for chunking text (breaking large text into smaller overlapping pieces)
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Specify the names of the models we will use
# The embedding model converts text into numbers (vectors)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# The LLM (Large Language Model) generates the actual chatbot responses
LLM_MODEL_NAME = "gemini-2.5-flash"

# Retrieve the Google Gemini API key from the environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if the API key is missing. If it is, stop the program with an error message
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Please make sure your .env file is set up correctly.")

# A list of web pages to scrape for GitLab Direction content
DIRECTION_PAGE_URLS = [
    "https://about.gitlab.com/direction/",
    "https://about.gitlab.com/direction/ai-powered/",
    "https://about.gitlab.com/direction/plan/",
    "https://about.gitlab.com/direction/create/",
    "https://about.gitlab.com/direction/secure/"
]
