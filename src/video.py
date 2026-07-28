import logging
import re

from src.client import ActorError, run_actor
from src.models import VideoMetadata

logger = logging.getLogger(__name__)

_ACTOR_ID = "h7sDV53CddomktSi5"
_CHANNEL_ACTOR_ID = "67Q6fmd8iedTVcCwY"


def _extract_tags(item: dict) -> list[str]:
    tags = item.get("hashtags")
    if isinstance(tags, list):
        return tags
    if isinstance(tags, str):
        return [tags]
    text = item.get("text", "")
    if not text:
        return []
    seen: set[str] = set()
    result: list[str] = []
    for word in text.split():
        if word.startswith("#") and len(word) > 1:
            clean = word.rstrip(".,!?;:")
            if clean not in seen:
                seen.add(clean)
                result.append(clean)
    return result


def get_video_metadata(video_url: str) -> VideoMetadata:
    logger.info("Fetching video metadata for %s", video_url)
    if not video_url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid video URL: {video_url}")
    run_input = {
        "startUrls": [{"url": video_url}],
        "maxResults": 1,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
    }
    try:
        items = run_actor(_ACTOR_ID, run_input)
    except ActorError:
        raise
    if not items:
        raise ActorError("No data returned for this video (private, deleted, or invalid URL)")
    item = items[0]
    title = item.get("title", "")
    if not title:
        raise ActorError("No title found — video may be private or deleted")
    return VideoMetadata(
        title=title,
        video_id=item.get("id", ""),
        video_url=item.get("url", video_url),
        description=item.get("description", ""),
        channel_name=item.get("channelName", ""),
        channel_url=item.get("channelUrl", ""),
        upload_date=item.get("date", ""),
        view_count=item.get("viewCount", 0),
        duration=item.get("duration", ""),
        thumbnail_url=item.get("thumbnailUrl", ""),
        tags=_extract_tags(item),
    )


def get_first_upload_year(channel_url: str) -> str:
    logger.info("Fetching first upload year for %s", channel_url)
    run_input = {
        "startUrls": [{"url": channel_url}],
        "maxResults": 1,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
        "sortVideosBy": "OLDEST",
    }
    try:
        items = run_actor(_CHANNEL_ACTOR_ID, run_input)
    except ActorError:
        return ""
    if not items:
        return ""
    date_str = items[0].get("date", "")
    if not date_str:
        return ""
    m = re.match(r"(\d{4})", date_str)
    return m.group(1) if m else ""
