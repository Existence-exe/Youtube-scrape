from src.models import ShortInfo
from src.statistics import (
    build_shorts_statistics,
    calculate_average_shorts_views,
    get_most_viewed_short,
    get_total_shorts,
)


def _s(**overrides):
    defaults = {"title": "S", "url": "", "view_count": 0, "upload_date": ""}
    defaults.update(overrides)
    return ShortInfo(**defaults)


class TestCalculateAverageShortsViews:
    def test_returns_zero_for_empty_list(self):
        assert calculate_average_shorts_views([]) == 0.0

    def test_returns_zero_when_no_valid_views(self):
        shorts = [_s(view_count="invalid"), _s(title="no view", view_count=0)]
        shorts[1].view_count = 0
        assert calculate_average_shorts_views(shorts) == 0.0

    def test_single_short(self):
        shorts = [_s(view_count=100)]
        assert calculate_average_shorts_views(shorts) == 100.0

    def test_multiple_shorts(self):
        shorts = [_s(view_count=100), _s(view_count=200), _s(view_count=300)]
        assert calculate_average_shorts_views(shorts) == 200.0

    def test_mixed_valid_and_invalid(self):
        shorts = [_s(view_count=100), _s(view_count="bad"), _s(view_count=200)]
        assert calculate_average_shorts_views(shorts) == 150.0


class TestGetMostViewedShort:
    def test_returns_none_for_empty_list(self):
        assert get_most_viewed_short([]) is None

    def test_returns_none_when_no_valid_views(self):
        shorts = [_s(view_count="invalid")]
        assert get_most_viewed_short(shorts) is None

    def test_single_short(self):
        shorts = [_s(title="Only", view_count=100)]
        result = get_most_viewed_short(shorts)
        assert result is not None
        assert result.title == "Only"
        assert result.view_count == 100

    def test_returns_short_with_highest_views(self):
        shorts = [
            _s(title="Low", view_count=50),
            _s(title="High", view_count=500),
            _s(title="Mid", view_count=200),
        ]
        result = get_most_viewed_short(shorts)
        assert result is not None
        assert result.title == "High"
        assert result.view_count == 500

    def test_ignores_invalid_views_when_finding_max(self):
        shorts = [
            _s(title="Valid", view_count=300),
            _s(title="Invalid", view_count="bad"),
            _s(title="Best", view_count=500),
        ]
        result = get_most_viewed_short(shorts)
        assert result is not None
        assert result.title == "Best"
        assert result.view_count == 500


class TestGetTotalShorts:
    def test_returns_zero_for_empty_list(self):
        assert get_total_shorts([]) == 0

    def test_returns_count(self):
        shorts = [_s(title="A"), _s(title="B"), _s(title="C")]
        assert get_total_shorts(shorts) == 3

    def test_handles_single_short(self):
        assert get_total_shorts([_s(title="Only")]) == 1


class TestBuildShortsStatistics:
    def test_builds_with_values(self):
        shorts = [_s(view_count=100), _s(view_count=200)]
        stats = build_shorts_statistics(shorts, "2020")
        assert stats.average_views == 150.0
        assert stats.total_shorts == 2
        assert stats.first_upload_year == "2020"

    def test_builds_with_empty_shorts(self):
        stats = build_shorts_statistics([])
        assert stats.average_views == 0.0
        assert stats.total_shorts == 0
        assert stats.first_upload_year == ""
