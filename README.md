# InstagramSummarizer

A Python pipeline that takes any public Instagram profile, downloads all posts/reels,
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

### 1. Install dependencies

```bash
pip install -r instagram_pipeline/requirements.txt
```

> **Note:** `ffmpeg` must also be installed on your system.  
> macOS: `brew install ffmpeg` | Ubuntu: `sudo apt install ffmpeg`

### 2. Configure

Edit `instagram_pipeline/config.py` (or use environment variables):

```python
INSTAGRAM_USERNAME = "nasa"          # Target public profile
GEMINI_API_KEY     = "YOUR_KEY"      # https://aistudio.google.com/app/apikey
WHISPER_MODEL      = "base"          # tiny / base / small / medium / large
MAX_POSTS          = 20              # Cap posts to process
```

### 3. Run

```bash
cd instagram_pipeline
python main.py
```

Or with environment variables:

```bash
INSTAGRAM_USERNAME=nasa GEMINI_API_KEY=your_key MAX_POSTS=10 python main.py
```

---

## Pipeline Steps

1. **Scrape** — Downloads posts via `instaloader` and saves `data/post_index.json`.
2. **Transcribe** — Extracts audio with `ffmpeg` and runs Whisper locally.
3. **Summarize** — Sends caption + transcript to Gemini; saves structured JSON.
4. **Cluster** — Groups all posts into 5–10 topic categories with Gemini.
5. **Export** — Writes per-topic `.md` files, a master `README.md`, and `all_posts.json`.

The pipeline is **resumable**: each step checks whether output already exists and skips
completed work, so you can safely re-run after interruptions.

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

| Variable | Default | Description |
|----------|---------|-------------|
| `INSTAGRAM_USERNAME` | `bbcnews` | Target Instagram profile |
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key |
| `WHISPER_MODEL` | `base` | Whisper model size |
| `MAX_POSTS` | `20` | Max posts to process |
| `OUTPUT_DIR` | `data` | Root output directory |

---

## License

MIT
