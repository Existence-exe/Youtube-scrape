from src.client import ActorError
from src.shorts import get_channel_shorts
from tests.conftest import mock_actor_call


def _item(**overrides):
    defaults = {
        "title": "Short Video",
        "video_url": "https://www.youtube.com/shorts/abc123",
        "views": 5000,
        "date_posted": "2024-03-10",
    }
    defaults.update(overrides)
    return defaults


class TestGetChannelShorts:
    def test_returns_list_of_shorts(self, mock_apify_client):
        items = [_item(), _item(title="Second", video_url="https://www.youtube.com/shorts/def456", views=3000)]
        mock_actor_call(mock_apify_client, items)
        result = get_channel_shorts("https://www.youtube.com/@channel")
        assert len(result) == 2
        assert result[0].title == "Short Video"
        assert result[0].url == "https://www.youtube.com/shorts/abc123"
        assert result[0].view_count == 5000
        assert result[0].upload_date == "2024-03-10"
        assert result[1].title == "Second"
        assert result[1].view_count == 3000

    def test_returns_empty_list_when_no_shorts(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [])
        result = get_channel_shorts("https://www.youtube.com/@empty")
        assert result == []

    def test_missing_fields_default_to_empty(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"title": "Only Title"}])
        result = get_channel_shorts("https://www.youtube.com/@minimal")
        assert len(result) == 1
        assert result[0].title == "Only Title"
        assert result[0].url == ""
        assert result[0].view_count == 0
        assert result[0].upload_date == ""

    def test_raises_on_invalid_url(self, mock_apify_client):
        try:
            get_channel_shorts("not-a-url")
            assert False, "Expected ValueError"
        except ValueError:
            pass
