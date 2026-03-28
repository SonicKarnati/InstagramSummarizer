"""
Configuration file for the Instagram Content Intelligence Pipeline.
Set your credentials and settings here before running main.py.
"""

import os

# --- Target Instagram Profile ---
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "bbcnews")

# --- Google Gemini API Key ---
# Obtain a free key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# --- Whisper Model Size ---
# Options: "tiny", "base", "small", "medium", "large"
# "base" is a good balance between speed and accuracy for free-tier usage.
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")

# --- Processing Limits ---
# Maximum number of posts to download and process (set to None for no limit).
MAX_POSTS = int(os.environ.get("MAX_POSTS", "20"))

# --- Output Directory ---
# Root directory for all pipeline data.
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "data")

# --- Rate Limiting ---
# Seconds to sleep between Instagram requests to avoid being rate-limited.
SCRAPER_SLEEP_MIN = 3
SCRAPER_SLEEP_MAX = 5

# --- Gemini Rate Limiting ---
# Seconds to sleep between Gemini API calls (free tier limit).
GEMINI_SLEEP_SECONDS = 4
