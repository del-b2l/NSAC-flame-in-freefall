import re

CITE = re.compile(r"\[([^\[\]]+)\]")
SENT = re.compile(r"(?<=[.!?])\s+")
NUM = re.compile(r"\d+(?:\.\d+)?")
WORD = re.compile(r"[a-z]{4,}")
STOP = set(["that", "this", "with", "from", "were", "was", "which", "their", "there", "these", "those", "into", "while", "after", "before", "during", "about", "also", "more", "than", "only", "such", "very", "when", "where", "what", "each", "both"])


def numbers(text: str) -> set[float]:
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    return {float(n) for n in NUM.findall(text)}


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def words(text: str) -> set[str]:
    return {_stem(w) for w in WORD.findall(text.lower()) if w not in STOP}


def check_grounded(answer, sources, allowed_numbers=frozenset(),
                   implicit_source=None, min_overlap=0.5):
    """sources: {record_id: text}. Returns (ok, reason)."""
    if not answer or not answer.strip():
        return False, "empty answer"
    for sent in SENT.split(answer.strip()):
        body = CITE.sub("", sent).strip()
        if not body:
            continue
        cited = [c.strip() for g in CITE.findall(sent) for c in g.split(",")]
        if not cited and implicit_source:
            cited = [implicit_source]
        if not cited:
            return False, f"uncited sentence: {body[:70]}"
        if unknown := [c for c in cited if c not in sources]:
            return False, f"unknown ids {unknown}"
        src_text = " ".join(sources[c] for c in cited)
        if extra := numbers(body) - (set(allowed_numbers) | numbers(src_text)):
            return False, f"numbers not in cited records: {sorted(extra)}"
        w = words(body)
        if w:
            support = len(w & words(src_text)) / len(w)
            if support < min_overlap:
                return False, f"weak support ({support:.0%}): {body[:70]}"
    return True, ""