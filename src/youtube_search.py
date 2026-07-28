import logging

from src.client import ActorError, run_actor
from src.models import SearchResult

logger = logging.getLogger(__name__)

_ACTOR_ID = "h7sDV53CddomktSi5"


def search_videos(query: str, include_shorts: bool = True, max_results: int = 10) -> list[SearchResult]:
    logger.info("Searching videos for query: %s (include_shorts=%s)", query, include_shorts)
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    run_input = {
        "searchQueries": [query],
        "maxResults": max_results,
        # request some short results from the actor when requested
        "maxResultsShorts": max_results if include_shorts else 0,
        "maxResultStreams": 0,
        # actor only accepts 'video' or 'movie' for videoType; keep 'video' and rely on
        # maxResultsShorts to include shorts when requested
        "videoType": "video",
    }
    try:
        items = run_actor(_ACTOR_ID, run_input)
    except ActorError:
        raise
    results = []
    for item in items:
        is_short = bool(item.get("isShort") or item.get("is_short") or item.get("short"))
        results.append(
            SearchResult(
                title=item.get("title", ""),
                channel_name=item.get("channelName", ""),
                video_url=item.get("url", ""),
                view_count=item.get("viewCount", 0),
                duration=item.get("duration", ""),
                thumbnail_url=item.get("thumbnailUrl", ""),
                is_short=is_short,
            )
        )
    return results
