# config.py
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
import warnings

# Config
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

LOGO_DIR = 'logos'
CLASSIFIED_LOGOS_FOLDER = "logo_groups"
CSV_FILE = 'logos_with_images.csv'
LOG_FILE = f'logger_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv'


SESSION = requests.Session()
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
SESSION.mount("https://", adapter)
SESSION.mount("http://", adapter)
