from typing import List, Dict
import json

from dotenv import load_dotenv

load_dotenv()

from docs_store import DOCS
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

code_llm = ChatOpenAI(model="gpt-4o-mini")


def fetch_docs(query: str, k: int = 3) -> List[Dict[str, str]]:
    """
    Very simple semantic-ish search over the in-memory DOCS list.
    Scores by keyword overlap.
    """
    q = query.lower()
    scored = []
    for doc in DOCS:
        text = (doc["topic"] + " " + doc["content"]).lower()
        score = 0
        for word in q.split():
            if word in text:
                score += 1
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:k]]


def analyze_code_snippet(code: str, stage_info: str) -> Dict[str, str]:
    """
    Uses the LLM to give structured feedback on a code snippet.
    Returns JSON with issues, suggested fundamentals, and a high-level hint.
    """
    system = SystemMessage(
        content=(
            "You are a React/TypeScript code reviewer. "
            "Do NOT rewrite the full solution. "
            "Identify likely issues and concepts to revisit, and respond ONLY in valid JSON."
        )
    )
    human = HumanMessage(
        content=(
            f"User code:\n``````\n\n"
            f"Stage context:\n{stage_info}\n\n"
            "Return JSON:\n"
            "{\n"
            '  \"issues\": string,\n'
            '  \"suggested_fundamentals\": string,\n'
            '  \"high_level_hint\": string\n'
            "}\n"
        )
    )
    resp = code_llm.invoke([system, human])
    data = json.loads(resp.content)
    return data
