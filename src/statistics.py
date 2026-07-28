from src.models import ShortInfo, ShortsStatistics


def calculate_average_shorts_views(shorts: list[ShortInfo]) -> float:
    if not shorts:
        return 0.0
    views = [s.view_count for s in shorts if isinstance(s.view_count, (int, float))]
    if not views:
        return 0.0
    return sum(views) / len(views)


def get_most_viewed_short(shorts: list[ShortInfo]) -> ShortInfo | None:
    if not shorts:
        return None
    valid = [s for s in shorts if isinstance(s.view_count, (int, float))]
    if not valid:
        return None
    return max(valid, key=lambda s: s.view_count)


def get_total_shorts(shorts: list[ShortInfo]) -> int:
    return len(shorts)


def build_shorts_statistics(
    shorts: list[ShortInfo],
    first_upload_year: str = "",
) -> ShortsStatistics:
    return ShortsStatistics(
        average_views=calculate_average_shorts_views(shorts),
        total_shorts=get_total_shorts(shorts),
        first_upload_year=first_upload_year,
    )
