"""
Configuration file for the Instagram Content Intelligence Pipeline.
Set your credentials and settings here before running main.py.
"""

import os

from dotenv import load_dotenv

# Load variables from a .env file if one exists (values already in the
# environment take precedence, so this is safe in any deployment context).
load_dotenv()

# --- Target Instagram Profile ---
TARGET_PROFILE = os.getenv("TARGET_PROFILE", "bbcnews")
# Legacy alias kept for backward compatibility
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", TARGET_PROFILE)

# --- Instagram Login Credentials (optional but strongly recommended) ---
# Providing credentials avoids 403 Forbidden errors caused by Instagram's
# aggressive unauthenticated rate limits.
IG_LOGIN_USER = os.getenv("IG_LOGIN_USER", "")
IG_LOGIN_PASS = os.getenv("IG_LOGIN_PASS", "")

# --- Google Gemini API Key ---
# Obtain a free key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

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
