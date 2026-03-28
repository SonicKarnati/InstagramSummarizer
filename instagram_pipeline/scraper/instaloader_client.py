"""
instaloader_client.py
Downloads posts, reels, captions, and metadata from a public Instagram profile.
"""

import json
import os
import random
import time

import instaloader
from tqdm import tqdm


def scrape_profile(username: str, output_dir: str, max_posts: int | None = None,
                   sleep_min: int = 3, sleep_max: int = 5,
                   login_user: str = "", login_pass: str = "") -> list[dict]:
    """
    Download posts from an Instagram profile and save a post index.

    Args:
        username:   Instagram username of the target profile.
        output_dir: Root data directory (e.g. ``"data"``).
        max_posts:  Maximum number of posts to process. ``None`` means no limit.
        sleep_min:  Minimum seconds to sleep between requests.
        sleep_max:  Maximum seconds to sleep between requests.
        login_user: Instagram account username for authenticated requests.
                    Providing credentials is strongly recommended to avoid
                    403 Forbidden errors on unauthenticated requests.
        login_pass: Instagram account password for authenticated requests.

    Returns:
        A list of post metadata dicts.
    """
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    loader = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=True,
        post_metadata_txt_pattern="",
        dirname_pattern=os.path.join(raw_dir, "{profile}"),
        quiet=True,
    )

    print(f"[scraper] Loading profile: {username}")
    if login_user and login_pass:
        print(f"[scraper] Logging in as {login_user} …")
        loader.login(login_user, login_pass)
    profile = instaloader.Profile.from_username(loader.context, username)

    posts_metadata: list[dict] = []
    post_iter = profile.get_posts()

    with tqdm(desc="Scraping posts", unit="post") as pbar:
        for post in post_iter:
            if max_posts is not None and len(posts_metadata) >= max_posts:
                break

            shortcode = post.shortcode
            post_dir = os.path.join(raw_dir, username)
            os.makedirs(post_dir, exist_ok=True)

            # Download the post (video/image + sidecar)
            try:
                loader.download_post(post, target=post_dir)
            except Exception as exc:
                print(f"[scraper] Warning: could not download {shortcode}: {exc}")

            metadata = {
                "shortcode": shortcode,
                "caption": post.caption or "",
                "date_utc": post.date_utc.isoformat(),
                "typename": post.typename,
                "is_video": post.is_video,
                "video_url": post.video_url if post.is_video else None,
                "likes": post.likes,
                "comments": post.comments,
                "post_dir": post_dir,
            }
            posts_metadata.append(metadata)
            pbar.update(1)

            # Rate-limit to be polite to Instagram's servers
            time.sleep(random.uniform(sleep_min, sleep_max))

    index_path = os.path.join(output_dir, "post_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(posts_metadata, f, indent=2, ensure_ascii=False)

    print(f"[scraper] Saved {len(posts_metadata)} posts to {index_path}")
    return posts_metadata
