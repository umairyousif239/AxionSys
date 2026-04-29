import os
import logging

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".py", ".js", ".ts", ".java", ".go", ".cpp")
MAX_FILE_SIZE = 5_000_000 # 5MB

def is_valid_file(file_path:str) -> bool:
    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            logger.warning(f"Skipping large file: {file_path}")
            return False
    except OSError as e:
        logger.warning(f"Could not access file size: {file_path} ({e})")
        return False
    
    return True

def read_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        logger.warning(f"Skipping non-text file: {file_path}")
    
    except OSError as e:
        logger.warning(f"Skipping file due to OS error: {file_path} ({e})")
    
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {e}")
        raise
    
    return None

def load_repo(path):
    documents = []
    
    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith(SUPPORTED_EXTENSIONS):
                continue
            
            file_path = os.path.join(root, file)
            
            if not is_valid_file(file_path):
                continue
            
            content = read_file(file_path)
            if content is None:
                continue
            
            documents.append({
                "path": file_path,
                "content": content
            })
    
    return documents