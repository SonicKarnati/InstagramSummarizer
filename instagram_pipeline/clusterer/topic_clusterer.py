"""
topic_clusterer.py
Groups posts into major topic categories using Google Gemini.
"""

import json
import os
import re

import google.generativeai as genai


_CLUSTER_PROMPT_TEMPLATE = """
You are a content strategist. Below is a list of Instagram posts with their titles and topic tags.
Group them into 5-10 major content categories that best represent the overall themes.

Posts (JSON array):
{posts_json}

Return a JSON object with exactly this structure:
{{
  "categories": [
    {{
      "name": "Category Name",
      "description": "1-2 sentence description of this category",
      "post_ids": ["shortcode1", "shortcode2", ...]
    }}
  ]
}}

Rules:
- Every post must appear in at least one category.
- A post may belong to multiple categories if appropriate.
- Category names should be concise (2-4 words).
- Respond with ONLY the JSON object. Do not include markdown code fences or any other text.
"""


def _strip_markdown_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences from a string."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def cluster_topics(output_dir: str, api_key: str) -> dict:
    """
    Read all summary JSON files, send their titles and tags to Gemini, and
    save the resulting topic clusters.

    Args:
        output_dir: Root data directory (e.g. ``"data"``).
        api_key:    Google Gemini API key.

    Returns:
        The parsed cluster dict with a ``"categories"`` key.
    """
    summaries_dir = os.path.join(output_dir, "summaries")
    out_dir = os.path.join(output_dir, "output")
    os.makedirs(out_dir, exist_ok=True)

    # Load all summaries
    summaries: list[dict] = []
    for fname in sorted(os.listdir(summaries_dir)):
        if fname.endswith(".json"):
            with open(os.path.join(summaries_dir, fname), "r", encoding="utf-8") as f:
                summaries.append(json.load(f))

    if not summaries:
        print("[clusterer] No summaries found — skipping clustering.")
        return {"categories": []}

    # Build a compact representation for the prompt
    posts_for_prompt = [
        {
            "shortcode": s.get("shortcode", ""),
            "title": s.get("title", ""),
            "topic_tags": s.get("topic_tags", []),
            "content_type": s.get("content_type", ""),
        }
        for s in summaries
    ]

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = _CLUSTER_PROMPT_TEMPLATE.format(
        posts_json=json.dumps(posts_for_prompt, indent=2)
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        clean_text = _strip_markdown_fences(raw_text)
        clusters = json.loads(clean_text)
    except Exception as exc:
        print(f"[clusterer] Warning: clustering failed: {exc}")
        # Fallback: single category with all posts
        clusters = {
            "categories": [
                {
                    "name": "All Posts",
                    "description": "All posts from the profile.",
                    "post_ids": [s["shortcode"] for s in summaries],
                }
            ]
        }

    cluster_path = os.path.join(out_dir, "topic_clusters.json")
    with open(cluster_path, "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)

    print(f"[clusterer] Topic clusters saved to {cluster_path}")
    return clusters
