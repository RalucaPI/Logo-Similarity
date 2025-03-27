# logger.py
import inspect
import pandas as pd
from datetime import datetime
import os
from config import LOG_FILE

def log_event(action, status, error=""):
    line = inspect.currentframe().f_back.f_lineno
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_data = pd.DataFrame([[line, action, status, error, timestamp]],
                            columns=['Line', 'Action', 'Status', 'Error', 'Timestamp'])

    if not os.path.exists(LOG_FILE):
        log_data.to_csv(LOG_FILE, index=False)
    else:
        log_data.to_csv(LOG_FILE, mode='a', header=False, index=False)
