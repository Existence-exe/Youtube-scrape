import logging
from typing import Optional

from src.client import ActorError, run_actor
from src.models import ShortInfo

logger = logging.getLogger(__name__)

_SHORTS_ACTOR_ID = "65aDXHapxlrOSbbUP"
_MAX_SHORTS_PER_CHANNEL = 10000


def get_channel_shorts(channel_url: str, max_shorts: Optional[int] = None) -> list[ShortInfo]:
    logger.info("Fetching shorts for %s (max_shorts=%s)", channel_url, max_shorts)
    if not channel_url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid channel URL: {channel_url}")
    if max_shorts is None:
        max_shorts = _MAX_SHORTS_PER_CHANNEL
    try:
        max_shorts = int(max_shorts)
    except Exception:
        max_shorts = _MAX_SHORTS_PER_CHANNEL
    # enforce actor limit
    max_shorts = min(max_shorts, _MAX_SHORTS_PER_CHANNEL)
    run_input = {
        "channelUrls": [channel_url],
        "maxShortsPerChannel": max_shorts,
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
