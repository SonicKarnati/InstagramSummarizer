"""
gemini_summarizer.py
Summarizes post captions and transcripts using Google Gemini (free tier).
"""

import json
import os
import re
import time

import google.generativeai as genai
from tqdm import tqdm


_SUMMARY_PROMPT_TEMPLATE = """
You are a content analyst. Given the Instagram post caption and its transcript (if any),
return a JSON object with exactly the following keys:

- "title": short descriptive title (max 10 words)
- "topic_tags": list of 3-5 topic keyword strings
- "key_points": list of 2-4 key takeaway strings
- "main_claim": one-sentence main claim or message
- "content_type": one of "educational", "entertainment", "news", "lifestyle", "promotional", "other"
- "summary": 2-3 sentence summary

Caption:
{caption}

Transcript:
{transcript}

Respond with ONLY the JSON object. Do not include markdown code fences or any other text.
"""


def _strip_markdown_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences from a string."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def summarize_posts(output_dir: str, api_key: str,
                    sleep_seconds: float = 4.0) -> None:
    """
    Read ``post_index.json`` and the matching transcript files, then call the
    Gemini API to produce a structured summary for each post.

    Results are written to ``data/summaries/{shortcode}.json``.

    Args:
        output_dir:     Root data directory (e.g. ``"data"``).
        api_key:        Google Gemini API key.
        sleep_seconds:  Seconds to sleep between Gemini calls (rate-limit buffer).
    """
    summaries_dir = os.path.join(output_dir, "summaries")
    transcripts_dir = os.path.join(output_dir, "transcripts")
    os.makedirs(summaries_dir, exist_ok=True)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    index_path = os.path.join(output_dir, "post_index.json")
    with open(index_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in tqdm(posts, desc="Summarizing", unit="post"):
        shortcode = post["shortcode"]
        summary_path = os.path.join(summaries_dir, f"{shortcode}.json")

        # Skip already-summarized posts (resumable pipeline)
        if os.path.exists(summary_path):
            continue

        caption = post.get("caption", "") or ""

        transcript_path = os.path.join(transcripts_dir, f"{shortcode}.txt")
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
        else:
            transcript = ""

        prompt = _SUMMARY_PROMPT_TEMPLATE.format(
            caption=caption or "(no caption)",
            transcript=transcript or "(no transcript)",
        )

        try:
            response = model.generate_content(prompt)
            raw_text = response.text
            clean_text = _strip_markdown_fences(raw_text)
            summary_data = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            print(f"[summarizer] Warning: JSON parse error for {shortcode}: {exc}")
            summary_data = {
                "title": shortcode,
                "topic_tags": [],
                "key_points": [],
                "main_claim": "",
                "content_type": "other",
                "summary": caption[:200] if caption else "",
            }
        except Exception as exc:
            print(f"[summarizer] Warning: Gemini error for {shortcode}: {exc}")
            summary_data = {
                "title": shortcode,
                "topic_tags": [],
                "key_points": [],
                "main_claim": "",
                "content_type": "other",
                "summary": caption[:200] if caption else "",
            }

        summary_data["shortcode"] = shortcode
        summary_data["date_utc"] = post.get("date_utc", "")
        summary_data["likes"] = post.get("likes", 0)
        summary_data["comments"] = post.get("comments", 0)

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # Respect Gemini free-tier rate limit
        time.sleep(sleep_seconds)

    print(f"[summarizer] Summaries saved to {summaries_dir}")
