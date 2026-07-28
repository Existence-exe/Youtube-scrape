import logging

from src.client import ActorError, run_actor
from src.models import ShortInfo

logger = logging.getLogger(__name__)

_SHORTS_ACTOR_ID = "65aDXHapxlrOSbbUP"


def get_channel_shorts(channel_url: str) -> list[ShortInfo]:
    logger.info("Fetching shorts for %s", channel_url)
    if not channel_url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid channel URL: {channel_url}")
    run_input = {
        "channelUrls": [channel_url],
        "maxShortsPerChannel": 999999,
    }
    try:
        items = run_actor(_SHORTS_ACTOR_ID, run_input)
    except ActorError:
        raise
    return [
        ShortInfo(
            title=item.get("title", ""),
            url=item.get("video_url", ""),
            view_count=item.get("views", 0),
            upload_date=item.get("date_posted", ""),
        )
        for item in items
    ]
