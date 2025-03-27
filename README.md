# Logo Similarity
 
Logo Visual Grouping & Classification
This project provides an end-to-end pipeline for downloading company logos from domain names, extracting visual features, clustering logos based on similarity, logging the process, and organizing results in clearly separated folders.


## File	description

| File  | Description |
| ------------- | ------------- |
| config.py	  | Central configuration file with paths, session setup, retry logic  |
| logger.py  |Custom logging utility for structured CSV logs   |
|  extract_logos.py | Downloads logos from given domain names using Clearbit  |
| classify_logos.py  |  	Performs feature extraction and groups logos visually |
| utils.py  | 	Helper functions: cleanup, parquet-to-CSV, setup  |
| logger_*.csv  | Log file capturing each step of the process  |
| end_program.py  |  Script that deletes the logos/ folder after the logos have been grouped |
|  logos/ | Temporary folder storing downloaded raw logo images  |
| logo_groups/  | Output folder containing grouped logos by visual similarity  |





## Detailed file description

config.py
- Defines paths for LOGO_DIR, CLASSIFIED_LOGOS_FOLDER, CSV_FILE, LOG_FILE, and SESSION

- Sets up a requests.Session() with retry logic for stable Clearbit access

logger.py
- Defines log_event(action, status, error="")

- Each call writes to a CSV log file with the following columns:

- Line (source code line number), 
Action, 
Status (Started, Completed, Error, etc.), 
Error (optional), 
Timestamp

extract_logos.py
- Reads a CSV with a column like domain

- Downloads logos from the CSV file

- Saves each image to the logos/ folder

- Uses ThreadPoolExecutor for concurrent downloads

- Logs successes and failures via log_event

classify_logos.py
- Loads OpenAI's CLIP model

- Extracts image embeddings from all logos

- Computes cosine similarity matrix

- Applies HDBSCAN for unsupervised clustering

- Uses DBSCAN for fallback clustering of outliers

- Uses SSIM-based fallback for remaining ungrouped images

- Copies logos into logo_groups/group_X/ folders

- Logs each major step (feature extraction, clustering, fallback, etc.)

utils.py
   - cleanup():

     - Deletes the CSV file if it exists

     - Deletes both logos/ and logo_groups/ folders if present

     - Logs each action step-by-step

   - setup_directories():

     - Creates logos/ and logo_groups/ folders

   - parquet_to_csv():

     - Converts .parquet files to .csv

end_program.py
- Standalone script to clean only the logos/ folder

