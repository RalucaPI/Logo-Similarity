# main.py
from utils import cleanup, setup_directories, parquet_to_csv
from extract_logos import extract_logos
from classify_logos import  group_logos
from end_program import program_cleanup
if __name__ == "__main__":
    cleanup()
    parquet_to_csv("logos.snappy.parquet", "logos.csv")
    setup_directories()
    extract_logos("logos.csv")
    group_logos()
    program_cleanup()


