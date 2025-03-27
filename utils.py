# utils.py
import os
import pandas as pd
from logger import log_event

def cleanup():
    log_event("Start utils.py", "Started")
    log_event("Start cleanup", "Started")
    from config import CSV_FILE, LOGO_DIR, CLASSIFIED_LOGOS_FOLDER
    try:
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            log_event("Delete CSV file", "Success")

        if os.path.exists(LOGO_DIR):
            for file in os.listdir(LOGO_DIR):
                file_path = os.path.join(LOGO_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(LOGO_DIR)
            log_event("Delete logos directory", "Success")

        if os.path.exists(CLASSIFIED_LOGOS_FOLDER):
            for root, dirs, files in os.walk(CLASSIFIED_LOGOS_FOLDER, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(CLASSIFIED_LOGOS_FOLDER)
            log_event("Delete classified logos directory", "Success")

        os.makedirs(LOGO_DIR, exist_ok=True)
        log_event("Recreate logos directory", "Success")

    except Exception as e:
        log_event("Cleanup error", "Error", str(e))

    log_event("End cleanup", "Ended")

def parquet_to_csv(input_file, output_file):
    log_event("Convert file", "Started")
    try:
        df = pd.read_parquet(input_file, engine='auto')
        df.to_csv(output_file, index=False)
        log_event("Convert Parquet to CSV", "Success")
    except Exception as e:
        log_event("Convert Parquet to CSV", "Error", str(e))

def setup_directories():
    log_event("Set directories", "Started")
    from config import LOGO_DIR, CLASSIFIED_LOGOS_FOLDER
    os.makedirs(LOGO_DIR, exist_ok=True)
    os.makedirs(CLASSIFIED_LOGOS_FOLDER, exist_ok=True)

def normalize_domain(domain):
    domain = domain.strip()
    if not domain.startswith(('http://', 'https://')):
        return f"https://{domain}"
    return domain