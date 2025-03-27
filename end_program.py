import os
import shutil
from logger import log_event
from config import LOGO_DIR



def program_cleanup():
    log_event("Cleanup Program", "Started")

    try:
        if os.path.exists(LOGO_DIR):
            shutil.rmtree(LOGO_DIR)
            log_event("Cleanup Logos Folder", "Success", f"Deleted folder: {LOGO_DIR}")
        else:
            log_event("Cleanup Logos Folder", "Skipped", "Folder does not exist")

        log_event("Cleanup Program", "Completed")

    except Exception as e:
        log_event("Cleanup Logos Folder", "Error", str(e))
        log_event("Cleanup Program", "Failed")
