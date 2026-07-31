import logging
import time
import re
import os

from src.client import ActorError, test_connection
from src.report import generate_report
from src.shorts import get_channel_shorts
from src.statistics import build_shorts_statistics
from src.video import get_video_metadata, get_first_upload_year
from src.models import ChannelMetadata

logger = logging.getLogger(__name__)


def _print_separator(char: str = "=", width: int = 72) -> None:
    print(char * width)


def _print_header(text: str) -> None:
    _print_separator()
    print(f"  {text}")
    _print_separator()


def _display_shorts_table(shorts_list: list) -> None:
    if not shorts_list:
        print("No shorts found.")
        return
    print()
    print(f"{ '#':<3s} {'Title':50s} {'Views':>12s} {'Date':12s}")
    print("-" * 80)
    for i, s in enumerate(shorts_list, 1):
        title = s.title[:47] if len(s.title) > 47 else s.title
        views = f"{s.view_count:,}"
        date = s.upload_date or "N/A"
        print(f"{i:<3d} {title:50s} {views:>12s} {date:12s}")
    print()


def _display_short_report(video, shorts_stats) -> None:
    _print_header("SHORT METADATA")
    print(f"  {'Title':30s} {video.title}")
    print(f"  {'Video ID':30s} {video.video_id}")
    print(f"  {'Channel':30s} {video.channel_name}")
    print(f"  {'Upload Date':30s} {video.upload_date}")
    print(f"  {'View Count':30s} {video.view_count:,}")
    print(f"  {'Duration':30s} {video.duration}")

    _print_header("SHORTS STATISTICS")
    print(f"  {'Total Shorts':30s} {shorts_stats.total_shorts}")
    print(f"  {'Average Views':30s} {shorts_stats.average_views:,.1f}")
    print(f"  {'First Upload Year':30s} {shorts_stats.first_upload_year or 'N/A'}")


def _safe_filename(s: str, max_len: int = 50) -> str:
    # Replace anything not alnum, hyphen or underscore with underscore, and truncate.
    if not s:
        return "report"
    s = re.sub(r"[^A-Za-z0-9_-]", "_", s)
    return s[:max_len]


def _analyze_short(video_url: str) -> None:
    start = time.time()
    logger.info("Starting short analysis for %s", video_url)

    video = get_video_metadata(video_url)
    logger.info("Short metadata retrieved in %.2fs", time.time() - start)

    # Basic heuristic: treat videos with duration <= 60s as shorts when possible
    try:
        length_str = video.duration or ""
        # duration may be formatted like "0:45" or "45"; convert to seconds when possible
        seconds = 0
        if ":" in length_str:
            parts = [int(p) for p in length_str.split(":")]
            seconds = parts[-1] + (parts[-2] * 60 if len(parts) > 1 else 0)
        elif length_str.isdigit():
            seconds = int(length_str)
    except Exception:
        seconds = 0

    if seconds and seconds > 90:
        print("Warning: this video appears longer than a typical short — results may not be short-only.")

    shorts_list = []
    first_upload_year = ""
    if video.channel_url:
        try:
            shorts_list = get_channel_shorts(video.channel_url)
            logger.info("Shorts retrieved in %.2fs", time.time() - start)
            first_upload_year = get_first_upload_year(video.channel_url)
        except (ActorError, ValueError) as e:
            logger.warning("Shorts unavailable: %s", e)

    shorts_stats = build_shorts_statistics(shorts_list, first_upload_year)

    _display_short_report(video, shorts_stats)

    # Build a ChannelMetadata from video info so reports include channel fields when actor data
    # isn't available.
    channel = ChannelMetadata(
        channel_name=video.channel_name,
        channel_url=video.channel_url,
        subscriber_count=0,
        channel_id="",
        country="",
        description="",
        total_videos=0,
    )

    # construct a safe filename for this report
    basefn = video.video_id or video.title or "report"
    filename = f"report_{_safe_filename(basefn)}"

    report = generate_report(video, channel, shorts_stats, filename=filename)
    logger.info("Report generated in %.2fs (saved as %s)", time.time() - start, filename)
    print()
    print(f"  Reports saved to {os.path.join('output', filename + '.json')} and {os.path.join('output', filename + '.csv')}")


def _list_channel_shorts(channel_url: str) -> None:
    start = time.time()
    logger.info("Listing shorts for %s", channel_url)
    try:
        shorts_list = get_channel_shorts(channel_url)
    except (ActorError, ValueError) as e:
        logger.error("Failed to fetch shorts: %s", e)
        print(f"  Error fetching shorts: {e}")
        return

    shorts_stats = build_shorts_statistics(shorts_list, get_first_upload_year(channel_url))
    _display_shorts_table(shorts_list)
    _print_header("SHORTS STATISTICS")
    print(f"  {'Total Shorts':30s} {shorts_stats.total_shorts}")
    print(f"  {'Average Views':30s} {shorts_stats.average_views:,.1f}")
    print(f"  {'First Upload Year':30s} {shorts_stats.first_upload_year or 'N/A'}")
    logger.info("Listing completed in %.2fs", time.time() - start)


def main() -> None:
    print()
    _print_header("YouTube Shorts Analyzer — Shorts Only")
    print("  A focused tool for fetching and analyzing YouTube Shorts data.\n")

    conn = test_connection()
    if "error" in conn:
        print(f"  Connection error: {conn['error']}")
        return
    print(f"  Connected as {conn.get('username', 'unknown')}")
    print()

    while True:
        print("  [1] Analyze a Short by URL")
        print("  [2] List all Shorts for a Channel (by channel URL)")
        print("  [3] Exit")
        choice = input("  Choose an option: ").strip()

        if choice == "1":
            urls_input = input("  Enter one or more short video URLs (space-separated): ").strip()
            if not urls_input:
                print("  No URL(s) provided.")
                continue
            urls = urls_input.split()
            for url in urls:
                try:
                    _analyze_short(url)
                except (ActorError, ValueError) as e:
                    logger.error("Analysis failed for %s: %s", url, e)
                    print(f"  Analysis error for {url}: {e}")
                    continue

        elif choice == "2":
            channel = input("  Enter a channel URL: ").strip()
            if not channel:
                print("  No channel URL provided.")
                continue
            _list_channel_shorts(channel)

        elif choice == "3":
            print("  Goodbye.")
            break

        else:
            print("  Invalid option. Please choose 1, 2 or 3.")
        print()


if __name__ == "__main__":
    main()
