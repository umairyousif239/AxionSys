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
    "confidence": 0.0
}}
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
            "confidence": 0.0
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
            "confidence": 0.0
        }

    # ------------------------
    # SAFETY: enforce valid files
    # ------------------------
    valid_files = {r.get("file", "unknown_file") for r in reranked_results}

    if not data.get("affected_files"):
        data["affected_files"] = list(valid_files)[:2]
    else:
        # filter hallucinated files
        data["affected_files"] = [
            f for f in data["affected_files"] if f in valid_files
        ] or list(valid_files)[:2]

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