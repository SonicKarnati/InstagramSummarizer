"""
markdown_exporter.py
Writes the final knowledge base: per-topic Markdown files, a master README,
and a consolidated all_posts.json.
"""

import json
import os
from datetime import datetime, timezone


def _slugify(name: str) -> str:
    """Convert a category name to a filesystem-safe slug."""
    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "")
        .replace("?", "")
        .replace("&", "and")
    )


def _load_summaries(summaries_dir: str) -> dict[str, dict]:
    """Return a shortcode → summary dict from all JSON files in *summaries_dir*."""
    summaries: dict[str, dict] = {}
    if not os.path.isdir(summaries_dir):
        return summaries
    for fname in os.listdir(summaries_dir):
        if fname.endswith(".json"):
            with open(os.path.join(summaries_dir, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            shortcode = data.get("shortcode", fname[:-5])
            summaries[shortcode] = data
    return summaries


def _render_post_section(summary: dict) -> str:
    """Render a single post as a Markdown section."""
    shortcode = summary.get("shortcode", "unknown")
    title = summary.get("title", shortcode)
    date = summary.get("date_utc", "")[:10]
    content_type = summary.get("content_type", "other")
    likes = summary.get("likes", 0)
    comments = summary.get("comments", 0)
    main_claim = summary.get("main_claim", "")
    summary_text = summary.get("summary", "")
    key_points = summary.get("key_points", [])
    tags = summary.get("topic_tags", [])
    url = f"https://www.instagram.com/p/{shortcode}/"

    lines = [
        f"## {title}",
        "",
        f"- **Date:** {date}",
        f"- **Type:** {content_type}",
        f"- **Likes:** {likes} | **Comments:** {comments}",
        f"- **Post:** [{shortcode}]({url})",
        f"- **Tags:** {', '.join(tags) if tags else '—'}",
        "",
    ]

    if main_claim:
        lines += [f"> {main_claim}", ""]

    if summary_text:
        lines += [summary_text, ""]

    if key_points:
        lines.append("**Key Points:**")
        for point in key_points:
            lines.append(f"- {point}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def export(output_dir: str, instagram_username: str = "") -> None:
    """
    Generate all output files:
    - ``data/output/{topic_slug}.md`` — one Markdown file per topic cluster
    - ``data/output/README.md`` — master table of contents with stats
    - ``data/output/all_posts.json`` — consolidated list of all post summaries

    Args:
        output_dir:          Root data directory (e.g. ``"data"``).
        instagram_username:  Target profile username (used in README heading).
    """
    out_dir = os.path.join(output_dir, "output")
    summaries_dir = os.path.join(output_dir, "summaries")
    os.makedirs(out_dir, exist_ok=True)

    clusters_path = os.path.join(out_dir, "topic_clusters.json")
    if not os.path.exists(clusters_path):
        print("[exporter] topic_clusters.json not found — skipping Markdown export.")
        return

    with open(clusters_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    summaries = _load_summaries(summaries_dir)

    # --- Write per-topic Markdown files ---
    toc_lines: list[str] = []
    for category in clusters.get("categories", []):
        cat_name = category.get("name", "Uncategorized")
        cat_desc = category.get("description", "")
        post_ids: list[str] = category.get("post_ids", [])
        slug = _slugify(cat_name)
        md_filename = f"{slug}.md"
        md_path = os.path.join(out_dir, md_filename)

        lines = [
            f"# {cat_name}",
            "",
            f"> {cat_desc}" if cat_desc else "",
            "",
            f"*{len(post_ids)} post(s) in this category*",
            "",
            "---",
            "",
        ]

        for shortcode in post_ids:
            summary = summaries.get(shortcode)
            if summary:
                lines.append(_render_post_section(summary))
            else:
                lines.append(f"## {shortcode}\n\n*(Summary not available)*\n\n---\n")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        toc_lines.append(
            f"| [{cat_name}]({md_filename}) | {cat_desc} | {len(post_ids)} |"
        )

    # --- Write master README.md ---
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    profile_heading = (
        f"@{instagram_username}" if instagram_username else "Instagram Profile"
    )
    readme_lines = [
        f"# Instagram Knowledge Base — {profile_heading}",
        "",
        f"*Generated on {generated_at}*",
        "",
        "## Stats",
        "",
        f"- **Total posts processed:** {len(summaries)}",
        f"- **Topic categories:** {len(clusters.get('categories', []))}",
        "",
        "## Topics",
        "",
        "| Topic | Description | Posts |",
        "|-------|-------------|-------|",
        *toc_lines,
        "",
        "---",
        "*Generated by the Instagram Content Intelligence Pipeline.*",
    ]

    readme_path = os.path.join(out_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines))

    # --- Write all_posts.json ---
    all_posts_path = os.path.join(out_dir, "all_posts.json")
    with open(all_posts_path, "w", encoding="utf-8") as f:
        json.dump(list(summaries.values()), f, indent=2, ensure_ascii=False)

    print(f"[exporter] Wrote {len(clusters.get('categories', []))} topic files → {out_dir}")
    print(f"[exporter] Master README → {readme_path}")
    print(f"[exporter] all_posts.json → {all_posts_path}")
