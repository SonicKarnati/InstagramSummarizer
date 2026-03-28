"""
main.py
Entry point for the Instagram Content Intelligence Pipeline.

Usage:
    cd instagram_pipeline
    python main.py

    # Or override settings via environment variables:
    INSTAGRAM_USERNAME=nasa MAX_POSTS=10 python main.py
"""

import os
import sys

# Allow running directly from the instagram_pipeline directory
sys.path.insert(0, os.path.dirname(__file__))

import config  # noqa: E402
from scraper.instaloader_client import scrape_profile  # noqa: E402
from transcriber.whisper_transcriber import transcribe_posts  # noqa: E402
from summarizer.gemini_summarizer import summarize_posts  # noqa: E402
from clusterer.topic_clusterer import cluster_topics  # noqa: E402
from exporter.markdown_exporter import export  # noqa: E402


def validate_config() -> None:
    """Fail fast if required configuration values are missing."""
    if not config.INSTAGRAM_USERNAME:
        sys.exit("[main] ERROR: INSTAGRAM_USERNAME is not set in config.py")
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        sys.exit(
            "[main] ERROR: GEMINI_API_KEY is not configured. "
            "Set it in config.py or via the GEMINI_API_KEY environment variable."
        )


def main() -> None:
    validate_config()

    output_dir = config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(" Instagram Content Intelligence Pipeline")
    print("=" * 60)
    print(f"  Target profile : @{config.INSTAGRAM_USERNAME}")
    print(f"  Max posts      : {config.MAX_POSTS}")
    print(f"  Whisper model  : {config.WHISPER_MODEL}")
    print(f"  Output dir     : {output_dir}")
    print("=" * 60)

    # ── Step 1: Scrape ────────────────────────────────────────────
    index_path = os.path.join(output_dir, "post_index.json")
    if os.path.exists(index_path):
        print("\n[main] post_index.json already exists — skipping scrape step.")
        print("[main] Delete data/post_index.json to re-scrape.")
    else:
        print("\n[main] Step 1/5 — Scraping Instagram profile …")
        scrape_profile(
            username=config.INSTAGRAM_USERNAME,
            output_dir=output_dir,
            max_posts=config.MAX_POSTS,
            sleep_min=config.SCRAPER_SLEEP_MIN,
            sleep_max=config.SCRAPER_SLEEP_MAX,
            login_user=config.IG_LOGIN_USER,
            login_pass=config.IG_LOGIN_PASS,
        )

    # ── Step 2: Transcribe ────────────────────────────────────────
    print("\n[main] Step 2/5 — Transcribing video posts …")
    transcribe_posts(
        output_dir=output_dir,
        whisper_model_name=config.WHISPER_MODEL,
    )

    # ── Step 3: Summarize ─────────────────────────────────────────
    print("\n[main] Step 3/5 — Summarizing posts with Gemini …")
    summarize_posts(
        output_dir=output_dir,
        api_key=config.GEMINI_API_KEY,
        sleep_seconds=config.GEMINI_SLEEP_SECONDS,
    )

    # ── Step 4: Cluster ───────────────────────────────────────────
    print("\n[main] Step 4/5 — Clustering topics with Gemini …")
    cluster_topics(
        output_dir=output_dir,
        api_key=config.GEMINI_API_KEY,
    )

    # ── Step 5: Export ────────────────────────────────────────────
    print("\n[main] Step 5/5 — Exporting Markdown knowledge base …")
    export(
        output_dir=output_dir,
        instagram_username=config.INSTAGRAM_USERNAME,
    )

    print("\n" + "=" * 60)
    print(" Pipeline complete!")
    print(f" Output: {os.path.abspath(os.path.join(output_dir, 'output'))}")
    print("=" * 60)


if __name__ == "__main__":
    main()
