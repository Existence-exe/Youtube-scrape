from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class VideoMetadata:
    title: str = ""
    video_id: str = ""
    video_url: str = ""
    description: str = ""
    channel_name: str = ""
    channel_url: str = ""
    upload_date: str = ""
    view_count: int = 0
    duration: str = ""
    thumbnail_url: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChannelMetadata:
    channel_name: str = ""
    channel_url: str = ""
    subscriber_count: int = 0
    channel_id: str = ""
    country: str = ""
    description: str = ""
    total_videos: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShortInfo:
    title: str = ""
    url: str = ""
    view_count: int = 0
    upload_date: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchResult:
    title: str = ""
    channel_name: str = ""
    video_url: str = ""
    view_count: int = 0
    duration: str = ""
    thumbnail_url: str = ""
    is_short: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShortsStatistics:
    average_views: float = 0.0
    total_shorts: int = 0
    first_upload_year: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalyticsReport:
    video: VideoMetadata
    channel: ChannelMetadata
    shorts: ShortsStatistics

    def to_dict(self) -> dict[str, Any]:
        return {
            "video": self.video.to_dict(),
            "channel": self.channel.to_dict(),
            "shorts": self.shorts.to_dict(),
        }
