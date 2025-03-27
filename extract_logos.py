import pandas as pd
import os
from config import LOGO_DIR, SESSION, LOG_FILE
from datetime import datetime
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger import log_event

def download_logo(i, domain):

    if pd.isna(domain):
        return None

    url = f"https://logo.clearbit.com/{domain.strip()}"
    try:
        response = SESSION.get(url, timeout=10, verify=False)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img = img.resize((224, 224), Image.Resampling.LANCZOS)

        filename = f"logo_{i}_{domain.strip().replace('.', '_')}.png"
        filepath = os.path.join(LOGO_DIR, filename)
        img.save(filepath, format="PNG")

        print(f"[{i}] Downloaded: {filename}")
        return "success"

    except Exception as e:
        error_message = f"{datetime.now()}, {url}, {str(e)}"
        print(f"[{i}] Error at {url}: {e}")
        return error_message

def extract_logos(csv_file, domain_column='domain', max_threads=20):
    log_event("Extract Logos", "Started")

    try:
        os.makedirs(LOGO_DIR, exist_ok=True)

        try:
            df = pd.read_csv(csv_file)
            print(f"CSV loaded: {csv_file}")
            log_event("CSV Load", "Success", f"{len(df)} domains")
        except Exception as e:
            log_event("CSV Load", "Error", str(e))
            return

        errors = []
        success_count = 0

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [
                executor.submit(download_logo, i, row.get(domain_column))
                for i, row in df.iterrows()
            ]

            for future in as_completed(futures):
                result = future.result()
                if result == "success":
                    success_count += 1
                elif result:
                    errors.append(result)

        log_event("Extract Logos", "Completed", f"Success: {success_count}, Errors: {len(errors)}")

    except Exception as e:
        log_event("Extract Logos", "Error", str(e))

    log_event("End extract_logos.py", "Ended")


