import json
import re
from backend.services.llm import run_llm

def build_fix_prompt(root_cause: dict, chunks: list) -> str:
    affected_files = ", ".join(root_cause.get("affected_files", []))
    cause = root_cause.get("root_cause", "")

    context_parts = []
    for i, r in enumerate(chunks[:2]):
        file = r.get("file", "unknown")
        content = r.get("content", "").strip()

        if len(content) > 300:
            truncated = content[:300]
            last_newline = truncated.rfind("\n")
            content = truncated[:last_newline] if last_newline > 0 else truncated

        context_parts.append(f"[File: {file}]\n{content}")

    context = "\n\n".join(context_parts)

    return f"""You are a software engineer. Fix the bug described below.

Bug: {cause}
Affected Files: {affected_files}

Code:
{context}

Return ONLY valid JSON with these exact fields:
{{
    "diff": "unified diff string showing the fix",
    "explanation": "What was changed and why in 1-2 sentences.",
    "affected_file": "filename.py",
    "confidence": 0.9
}}

The diff field must start with --- and include +++ and @@ markers.
Do not include anything outside the JSON."""

def is_valid_diff(diff: str) -> bool:
    return (
        diff.strip().startswith("---")
        and "+++" in diff
        and "@@" in diff
    )

def generate_fix(root_cause: dict, reranked_chunks: list, top_k: int = 3) -> dict:
    if not root_cause or not reranked_chunks:
        return {
            "diff": "",
            "explanation": "Insufficient context to generate a fix.",
            "affected_file": "unknown",
            "confidence": 0.0
        }

    chunks = reranked_chunks[:top_k]
    prompt = build_fix_prompt(root_cause, chunks)

    try:
        response = run_llm("fix", prompt)
        cleaned = re.sub(r"```json|```", "", response).strip()
        data = json.loads(cleaned)

        diff = data.get("diff", "")
        if not is_valid_diff(diff):
            data["diff"] = ""
            data["diff_warning"] = "LLM returned malformed diff — explanation only."

        data["confidence"] = max(0.0, min(1.0, float(data.get("confidence", 0.0))))

        return data

    except Exception as e:
        return {
            "diff": "",
            "explanation": f"Fix generation failed: {str(e)}",
            "affected_file": "unknown",
            "confidence": 0.0
        }