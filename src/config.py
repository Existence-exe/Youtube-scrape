import logging
import os

from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable is not set")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "analytics.log")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
