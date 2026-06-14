import re
from typing import Literal

IntentType = Literal["sql_query", "graph_query", "profiling", "forecasting", "pdf_export"]

KEYWORDS = {
    "pdf_export":  ["export", "pdf", "download", "report", "print", "compile", "generate report"],
    "graph_query": ["connected", "network", "link", "associates", "who called", "who knows",
                    "relationship", "gang", "accomplice", "linked to", "related to"],
    "profiling":   ["pattern", "modus operandi", "mo", "similar case", "habitual",
                    "repeat offender", "same method", "profile", "demographic", "correlation"],
    "forecasting": ["predict", "forecast", "future", "next month", "next week", "trend",
                    "spike", "will there be", "expect", "upcoming", "projection"],
}

def classify_intent(question: str) -> IntentType:
    q = question.lower().strip()
    for intent, kws in KEYWORDS.items():
        for kw in kws:
            if re.search(r"\b" + re.escape(kw) + r"\b", q):
                return intent
    return "sql_query"

def classify_with_confidence(question: str) -> dict:
    q = question.lower().strip()
    scores = {
        intent: sum(1 for kw in kws if re.search(r"\b" + re.escape(kw) + r"\b", q))
        for intent, kws in KEYWORDS.items()
    }
    if not any(scores.values()):
        return {"intent": "sql_query", "confidence": 0.5, "matched": []}
    best = max(scores, key=scores.get)
    matched = [kw for kw in KEYWORDS[best]
               if re.search(r"\b" + re.escape(kw) + r"\b", q)]
    return {"intent": best, "confidence": round(scores[best] / max(sum(scores.values()), 1), 2), "matched": matched}