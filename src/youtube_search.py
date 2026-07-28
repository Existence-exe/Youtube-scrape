import logging

from src.client import ActorError, run_actor
from src.models import SearchResult

logger = logging.getLogger(__name__)

_ACTOR_ID = "h7sDV53CddomktSi5"


def search_videos(query: str) -> list[SearchResult]:
    logger.info("Searching videos for query: %s", query)
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    run_input = {
        "searchQueries": [query],
        "maxResults": 10,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
        "videoType": "video",
    }
    try:
        items = run_actor(_ACTOR_ID, run_input)
    except ActorError:
        raise
    return [
        SearchResult(
            title=item.get("title", ""),
            channel_name=item.get("channelName", ""),
            video_url=item.get("url", ""),
            view_count=item.get("viewCount", 0),
            duration=item.get("duration", ""),
            thumbnail_url=item.get("thumbnailUrl", ""),
        )
        for item in items
    ]
