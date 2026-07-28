import logging

from src.client import ActorError, run_actor
from src.models import ChannelMetadata

logger = logging.getLogger(__name__)

_CHANNEL_ACTOR_ID = "67Q6fmd8iedTVcCwY"


def get_channel_metadata(channel_url: str) -> ChannelMetadata:
    logger.info("Fetching channel metadata for %s", channel_url)
    if not channel_url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid channel URL: {channel_url}")
    run_input = {
        "startUrls": [{"url": channel_url}],
        "maxResults": 1,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
    }
    try:
        items = run_actor(_CHANNEL_ACTOR_ID, run_input)
    except ActorError:
        raise
    if not items:
        raise ActorError("No data returned for this channel")
    item = items[0]
    return ChannelMetadata(
        channel_name=item.get("channelName", ""),
        channel_url=item.get("channelUrl") or channel_url,
        subscriber_count=item.get("numberOfSubscribers", 0),
        channel_id=item.get("channelId", ""),
        country=item.get("channelLocation", ""),
        description=item.get("channelDescription", ""),
        total_videos=item.get("channelTotalVideos", 0),
    )
