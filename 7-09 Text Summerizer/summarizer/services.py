import re
from collections import Counter

import requests
from django.conf import settings


class SummarizationError(Exception):
    pass


def _extract_sentences(text: str):
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]


def _summarize_locally(text: str, style: str) -> str:
    sentences = _extract_sentences(text)
    if not sentences:
        raise SummarizationError("The text is empty or unreadable.")

    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has",
        "he", "her", "his", "i", "in", "is", "it", "its", "of", "on", "or", "that",
        "the", "their", "them", "they", "this", "to", "was", "were", "will", "with",
        "you", "your", "we", "our", "us"
    }

    word_scores = Counter()
    for sentence in sentences:
        words = re.findall(r"\b\w+\b", sentence.lower())
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_scores[word] += 1

    if not word_scores:
        return sentences[0]

    scored = []
    for sentence in sentences:
        sentence_words = re.findall(r"\b\w+\b", sentence.lower())
        score = sum(word_scores.get(word, 0) for word in sentence_words if word not in stop_words)
        scored.append((score, sentence))

    sorted_sentences = [sentence for _, sentence in sorted(scored, key=lambda item: item[0], reverse=True)]
    if style == "concise":
        summary_sentences = sorted_sentences[:2]
        return " ".join(summary_sentences)
    if style == "detailed":
        summary_sentences = sorted_sentences[:4]
        takeaways = []
        for sentence in sorted_sentences[:3]:
            takeaways.append(f"- {sentence[:120].rstrip()}.")
        return " ".join(summary_sentences) + "\n\nKey takeaways:\n" + "\n".join(takeaways)

    summary_sentences = sorted_sentences[:3]
    takeaways = []
    for sentence in sorted_sentences[:3]:
        takeaways.append(f"- {sentence[:120].rstrip()}.")
    return " ".join(summary_sentences) + "\n\nKey takeaways:\n" + "\n".join(takeaways)


def summarize_with_qwen(text: str, style: str) -> str:
    length_instruction = {
        "concise": "in 3 to 5 crisp bullet points",
        "balanced": "in a short paragraph followed by 3 key takeaways",
        "detailed": "with a clear overview and 5 key takeaways",
    }[style]
    prompt = (
        "You are a precise text summarizer. Summarize the user's text in the same "
        "language as the input. Do not invent facts. Return only the summary, "
        f"{length_instruction}.\n\nTEXT:\n{text}"
    )
    try:
        response = requests.post(
            f"{settings.OLLAMA_URL.rstrip('/')}/api/generate",
            json={
                "model": settings.QWEN_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return _summarize_locally(text, style)
    except requests.exceptions.Timeout as exc:
        raise SummarizationError("Qwen took too long to respond. Please try again.") from exc
    except requests.exceptions.RequestException:
        return _summarize_locally(text, style)

    if not result:
        return _summarize_locally(text, style)
    return result
