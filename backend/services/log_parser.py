import re
from backend.services.llm import run_llm
import json

TRACEBACK_PATTERN = re.compile(
    r"Traceback \(most recent call last\):.*?((?:\w+\.)*\w*(?:Error|Exception|Warning)[^\n]*)",
    re.DOTALL
)

LOG_ERROR_PATTERN = re.compile(
    r"(?:ERROR|CRITICAL|FATAL)[^\n]*",
    re.IGNORECASE
)

FILE_LINE_PATTERN = re.compile(
    r'File "([^"]+)", line (\d+), in (\w+)'
)

def extract_tracebacks(text: str) -> list[dict]:
    results = []
    text = re.sub(r"^\s*[~^]+\s*$", "", text, flags=re.MULTILINE)
    for match in TRACEBACK_PATTERN.finditer(text):
        block = match.group(0)
        error_line = match.group(1).strip()
        
        file_refs = FILE_LINE_PATTERN.findall(block)
        
        results.append({
            "type": "traceback",
            "raw": block,
            "error": error_line,
            "files": [
                {"file": f, "line": int(l), "function": fn}
                for f, l, fn in file_refs
            ]
        })
    return results

def extract_log_errors(text: str) -> list[dict]:
    results = []
    for match in LOG_ERROR_PATTERN.finditer(text):
        results.append({
            "type": "log_error",
            "raw": match.group(0).strip(),
            "error": match.group(0).strip(),
            "files": []
        })
    return results

def extract_errors(text: str) -> list[dict]:
    errors = extract_tracebacks(text)
    if not errors:
        errors = extract_log_errors(text)
    if not errors:
        errors = [{
            "type": "free_form",
            "raw": text.strip(),
            "error": text.strip(),
            "files": []
        }]
    return errors

def generate_queries(error: dict) -> dict:
    error_text = error.get("error", "")
    files = error.get("files", [])

    file_context = ""
    if files:
        last = files[-1]
        file_context = f"function: {last['function']}, file: {last['file']}"

    prompt = f"""Generate short code search queries for this error.

Error: {error_text}
{f"Location: {file_context}" if file_context else ""}

Rules:
- primary query must be under 8 words
- secondary queries must be under 8 words each
- queries must be plain English, no code, no symbols
- focus on the failure and the function involved

Return ONLY valid JSON:
{{
    "primary": "short plain English query",
    "secondary": ["query two", "query three"]
}}"""

    try:
        response = run_llm("query_gen", prompt)
        cleaned = re.sub(r"```json|```", "", response).strip()
        data = json.loads(cleaned)
        return {
            "primary": data.get("primary", error_text),
            "secondary": data.get("secondary", [])[:2]
        }
    except Exception:
        primary = error_text[:120]
        secondary = []
        if files:
            last = files[-1]
            secondary.append(f"{last['function']} failure")
            if len(files) > 1:
                secondary.append(f"error in {files[-2]['function']}")
        return {
            "primary": primary,
            "secondary": secondary
        }

def parse_log(text: str) -> list[dict]:
    errors = extract_errors(text)
    results = []
    for error in errors:
        queries = generate_queries(error)
        results.append({
            "error": error["error"],
            "type": error["type"],
            "files_mentioned": error["files"],
            "primary_query": queries["primary"],
            "secondary_queries": queries["secondary"],
            "raw": error["raw"]
        })
    return results