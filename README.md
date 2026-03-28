# InstagramSummarizer

A Python pipeline that takes any Instagram profile, downloads all posts/reels,
transcribes video/audio, summarizes everything with Google Gemini (free tier), clusters
content by topic, and outputs a clean structured knowledge base in Markdown + JSON.

---

## Stack

| Layer | Library |
|-------|---------|
| Instagram scraping | `instaloader` |
| Audio extraction | `ffmpeg` |
| Speech-to-text | `openai-whisper` (local) |
| AI summarization & clustering | Google Gemini API (`gemini-1.5-flash`) |
| Output | Markdown files + JSON |

---

## Project Structure

```
instagram_pipeline/
│
├── main.py                      # Entry point — runs the full pipeline
├── config.py                    # API keys, settings, profile target
├── requirements.txt
│
├── scraper/
│   └── instaloader_client.py    # Downloads posts, reels, captions, metadata
│
├── transcriber/
│   └── whisper_transcriber.py   # Extracts audio from video, runs Whisper
│
├── summarizer/
│   └── gemini_summarizer.py     # Sends transcript+caption to Gemini
│
├── clusterer/
│   └── topic_clusterer.py       # Groups posts by topic using Gemini
│
├── exporter/
│   └── markdown_exporter.py     # Writes .md files and JSON
│
└── data/
    ├── raw/                     # Downloaded videos/images/captions
    ├── transcripts/             # .txt — one per post
    ├── summaries/               # .json — one per post
    └── output/                  # Final knowledge base files
```

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r instagram_pipeline/requirements.txt
```

> **Note:** `ffmpeg` must also be installed on your system.  
> macOS: `brew install ffmpeg` | Ubuntu: `sudo apt install ffmpeg` | Windows: https://ffmpeg.org/download.html

### 3. Configure credentials

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholders:

```dotenv
IG_LOGIN_USER=your_instagram_username   # Your Instagram username
IG_LOGIN_PASS=your_instagram_password   # Your Instagram password
TARGET_PROFILE=bbcnews                  # The profile you want to analyse
GEMINI_API_KEY=your_gemini_api_key      # https://aistudio.google.com/app/apikey
```

> **Why log in?**  
> Instagram aggressively rate-limits unauthenticated requests and will return
> `403 Forbidden` / `ProfileNotExistsException` for perfectly public profiles.
> Providing your Instagram login credentials lets `instaloader` authenticate
> before fetching the profile, which avoids these blocks entirely.
> Your credentials are only stored locally in your `.env` file and are never
> transmitted anywhere other than Instagram's own servers.

### 4. Run the pipeline

```bash
cd instagram_pipeline
python main.py
```

The pipeline is **resumable**: each step checks whether output already exists and skips
completed work, so you can safely re-run after interruptions.

---

## Pipeline Steps

1. **Scrape** — Downloads posts via `instaloader` and saves `data/post_index.json`.
2. **Transcribe** — Extracts audio with `ffmpeg` and runs Whisper locally.
3. **Summarize** — Sends caption + transcript to Gemini; saves structured JSON.
4. **Cluster** — Groups all posts into 5–10 topic categories with Gemini.
5. **Export** — Writes per-topic `.md` files, a master `README.md`, and `all_posts.json`.

---

## Output

After a successful run, `data/output/` contains:

| File | Description |
|------|-------------|
| `README.md` | Master table of contents with stats |
| `{topic}.md` | One Markdown file per topic cluster |
| `topic_clusters.json` | Raw clustering result from Gemini |
| `all_posts.json` | Every post summary in one JSON array |

---

## Environment Variables

All settings can be controlled via the `.env` file or by exporting environment variables
directly. Values already present in the environment take precedence over the `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_PROFILE` | `bbcnews` | Instagram profile to analyse |
| `IG_LOGIN_USER` | *(empty)* | Your Instagram username (recommended) |
| `IG_LOGIN_PASS` | *(empty)* | Your Instagram password (recommended) |
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key |
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`/`base`/`small`/`medium`/`large`) |
| `MAX_POSTS` | `20` | Max posts to process |
| `OUTPUT_DIR` | `data` | Root output directory |

---

## License

MIT

