import os
from dotenv import load_dotenv

load_dotenv()

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
DEFAULT_DOC_COUNT = int(os.getenv("DOC_COUNT", "100"))
