from backend.services.llm import run_llm
import json
import re

def _extract_json(text):
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group())


def rerank(query, results):
    formatted = "\n".join(
        f"[{i}] {r['content'][:600]}"
        for i, r in enumerate(results)
    )

    prompt = f"""
You are a relevance scorer for code search.

Query:
{query}

Snippets:
{formatted}

Return ONLY JSON:

{{
  "scores": [
    {{"idx": 0, "score": 0.0}},
    {{"idx": 1, "score": 0.0}}
  ]
}}

Rules:
- score must be 0.0 to 1.0
- do NOT reorder
- only evaluate relevance
"""

    try:
        response = run_llm("rerank", prompt)
        data = _extract_json(response)

        scores = data.get("scores", [])

        for item in scores:
            idx = item["idx"]
            if 0 <= idx < len(results):
                results[idx]["rerank_score"] = float(item["score"])

        return results

    except Exception:
        return results