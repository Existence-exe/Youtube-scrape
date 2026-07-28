import logging
import time

from src.channel import get_channel_metadata
from src.client import ActorError, test_connection
from src.report import generate_report
from src.shorts import get_channel_shorts
from src.statistics import build_shorts_statistics
from src.video import get_first_upload_year, get_video_metadata
from src.youtube_search import search_videos

logger = logging.getLogger(__name__)


def _print_separator(char: str = "=", width: int = 72) -> None:
    print(char * width)


def _print_header(text: str) -> None:
    _print_separator()
    print(f"  {text}")
    _print_separator()


def _print_search_table(results: list) -> None:
    if not results:
        print("No results found.")
        return
    print()
    print(f"{'#':<3s} {'Title':50s} {'Channel':25s} {'Views':>12s} {'Duration':10s}")
    print("-" * 102)
    for i, r in enumerate(results, 1):
        title = r.title[:47] if len(r.title) > 47 else r.title
        channel = r.channel_name[:22] if len(r.channel_name) > 22 else r.channel_name
        views = f"{r.view_count:,}"
        print(f"{i:<3d} {title:50s} {channel:25s} {views:>12s} {r.duration:10s}")
    print()


def _display_analytics_report(video, channel, shorts_stats) -> None:
    _print_header("VIDEO METADATA")
    print(f"  {'Title':30s} {video.title}")
    print(f"  {'Video ID':30s} {video.video_id}")
    print(f"  {'Channel':30s} {video.channel_name}")
    print(f"  {'Upload Date':30s} {video.upload_date}")
    print(f"  {'View Count':30s} {video.view_count:,}")
    print(f"  {'Duration':30s} {video.duration}")
    print(f"  {'Description':30s} {video.description[:100] if video.description else 'N/A'}...")
    print(f"  {'Tags':30s} {', '.join(video.tags) if video.tags else 'None'}")

    _print_header("CHANNEL METADATA")
    print(f"  {'Channel Name':30s} {channel.channel_name}")
    print(f"  {'Subscribers':30s} {channel.subscriber_count:,}")
    print(f"  {'Total Videos':30s} {channel.total_videos:,}")
    print(f"  {'Channel ID':30s} {channel.channel_id}")
    print(f"  {'Country':30s} {channel.country or 'N/A'}")
    print(f"  {'Description':30s} {channel.description[:100] if channel.description else 'N/A'}...")

    _print_header("SHORTS STATISTICS")
    print(f"  {'Total Shorts':30s} {shorts_stats.total_shorts}")
    print(f"  {'Average Views':30s} {shorts_stats.average_views:,.1f}")
    print(f"  {'First Upload Year':30s} {shorts_stats.first_upload_year or 'N/A'}")


def _run_analysis(video_url: str) -> None:
    start = time.time()
    logger.info("Starting analysis for %s", video_url)

    video = get_video_metadata(video_url)
    logger.info("Video metadata retrieved in %.2fs", time.time() - start)

    channel = None
    if video.channel_url:
        try:
            channel = get_channel_metadata(video.channel_url)
            logger.info("Channel metadata retrieved in %.2fs", time.time() - start)
        except (ActorError, ValueError) as e:
            logger.warning("Channel metadata unavailable: %s", e)
            channel = None

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

    if channel is None:
        channel = type("EmptyChannel", (), {
            "channel_name": video.channel_name,
            "channel_url": video.channel_url,
            "subscriber_count": 0,
            "total_videos": 0,
            "channel_id": "",
            "country": "",
            "description": "",
        })()

    _display_analytics_report(video, channel, shorts_stats)

    report = generate_report(video, channel, shorts_stats)
    logger.info("Report generated in %.2fs", time.time() - start)
    print()
    print(f"  Reports saved to output/report.json and output/report.csv")


def main() -> None:
    print()
    _print_header("YouTube Analyzer")
    print("  A tool for fetching and analyzing YouTube video data.\n")

    conn = test_connection()
    if "error" in conn:
        print(f"  Connection error: {conn['error']}")
        return
    print(f"  Connected as {conn.get('username', 'unknown')}")
    print()

    while True:
        print("  [1] Search YouTube")
        print("  [2] Exit")
        choice = input("  Choose an option: ").strip()

        if choice == "1":
            query = input("  Enter a search query: ").strip()
            if not query:
                print("  No query provided.")
                continue
            try:
                results = search_videos(query)
            except (ActorError, ValueError) as e:
                logger.error("Search failed: %s", e)
                print(f"  Search error: {e}")
                continue
            _print_search_table(results)
            if not results:
                continue
            pick = input("  Choose a video number: ").strip()
            try:
                idx = int(pick) - 1
                if idx < 0 or idx >= len(results):
                    print("  Invalid selection.")
                    continue
            except ValueError:
                print("  Invalid selection.")
                continue
            video_url = results[idx].video_url
            if not video_url:
                print("  Selected video has no URL.")
                continue
            print()
            try:
                _run_analysis(video_url)
            except (ActorError, ValueError) as e:
                logger.error("Analysis failed: %s", e)
                print(f"  Analysis error: {e}")
                continue

        elif choice == "2":
            print("  Goodbye.")
            break

        else:
            print("  Invalid option. Please choose 1 or 2.")
        print()


if __name__ == "__main__":
    main()
