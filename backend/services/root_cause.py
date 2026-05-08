import json
from backend.services.llm import run_llm


# ------------------------
# CONTEXT BUILDER
# ------------------------
def build_context(results, max_chunks=3):
    context_parts = []

    for i, r in enumerate(results[:max_chunks]):
        content = r.get("content", "")
        file = r.get("file", "unknown_file")

        hybrid = r.get("hybrid_score", 0.0)
        rerank = r.get("rerank_score", 0.0)
        final = r.get("final_score", hybrid)

        # safety
        if isinstance(content, dict):
            content = str(content)

        context_parts.append(f"""
[Chunk {i}]
File: {file}
Scores: hybrid={hybrid:.3f}, rerank={rerank:.3f}, final={final:.3f}

Content:
{content[:400]}
""")

    return "\n".join(context_parts)


# ------------------------
# PROMPT BUILDER
# ------------------------
def build_prompt(query, context):
    return f"""
You are a senior software debugging expert.

A user reports:
"{query}"

You are given ranked code snippets (higher score = more relevant).

{context}

TASK:
1. Identify the TRUE root cause (not symptoms)
2. Connect multiple files if needed
3. Explain WHY the failure occurs step-by-step
4. Suggest a concrete fix
5. Extract the call chain as an ordered list of files from entry point to bug location

STRICT RULES:
- Only reference files present in the context
- Do NOT invent files or functions
- Use snippet evidence
- Prefer higher-scoring snippets when reasoning

Return ONLY valid JSON:

{{
    "root_cause": "...",
    "affected_files": ["file1.py"],
    "reasoning": "...",
    "fix": "...",
    "confidence": 0.0,
    "call_chain": [
        {{"file": "entry.py", "function": "entry_function", "status": "ok"}},
        {{"file": "middle.py", "function": "middle_function", "status": "ok"}},
        {{"file": "buggy.py", "function": "buggy_function", "status": "bug"}}
    ]
}}

Status must be "ok", "bug", or "crash" for each file in the chain.
"bug" = where the root cause originates
"crash" = where the exception is raised
"ok" = passes through but not the source
"""


# ------------------------
# MAIN FUNCTION
# ------------------------
def generate_root_cause(query, reranked_results, top_k=3):
    if not reranked_results:
        return {
            "root_cause": "No results retrieved.",
            "affected_files": [],
            "reasoning": "",
            "fix": "",
            "confidence": 0.0,
            "call_chain": []
        }

    context = build_context(reranked_results, max_chunks=top_k)
    prompt = build_prompt(query, context)

    response = run_llm("root_cause", prompt)

    try:
        data = json.loads(response)
    except Exception:
        data = {
            "root_cause": "Failed to parse LLM output.",
            "affected_files": [],
            "reasoning": response[:500],
            "fix": "N/A",
            "confidence": 0.0,
            "call_chain": []
        }

    # validate affected files
    valid_files = {r.get("file", "unknown_file") for r in reranked_results}

    if not data.get("affected_files"):
        data["affected_files"] = list(valid_files)[:2]
    else:
        data["affected_files"] = [
            f for f in data["affected_files"] if f in valid_files
        ] or list(valid_files)[:2]

    # validate call chain
    if not data.get("call_chain"):
        # fallback: build chain from affected files
        data["call_chain"] = [
            {"file": f, "function": "unknown", "status": "bug" if i == len(data["affected_files"]) - 1 else "ok"}
            for i, f in enumerate(data["affected_files"])
        ]
    else:
        # ensure status values are valid
        valid_statuses = {"ok", "bug", "crash"}
        for node in data["call_chain"]:
            if node.get("status") not in valid_statuses:
                node["status"] = "ok"

    return data


# ------------------------
# LEGACY PARSER (optional)
# ------------------------
def parse_root_cause(text: str):
    root = ""
    explanation = ""

    lines = text.splitlines()
    mode = None

    for line in lines:
        if "root cause" in line.lower():
            mode = "root"
            continue
        elif "explanation" in line.lower():
            mode = "explanation"
            continue

        if mode == "root":
            root += line.strip() + " "
        elif mode == "explanation":
            explanation += line.strip() + " "

    return {
        "root_cause": root.strip(),
        "explanation": explanation.strip()
    }