from src.channel import get_channel_metadata
from src.client import ActorError
from tests.conftest import mock_actor_call


def _item(**overrides):
    defaults = {
        "channelName": "Test Channel",
        "channelUrl": "https://www.youtube.com/@test",
        "numberOfSubscribers": 50000,
        "channelTotalVideos": 1200,
        "channelId": "UCtest123",
        "channelDescription": "Test channel description",
        "channelLocation": "United States",
    }
    defaults.update(overrides)
    return defaults


class TestGetChannelMetadata:
    def test_returns_all_fields(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item()])
        result = get_channel_metadata("https://www.youtube.com/@test")
        assert result.channel_name == "Test Channel"
        assert result.channel_url == "https://www.youtube.com/@test"
        assert result.subscriber_count == 50000
        assert result.total_videos == 1200
        assert result.channel_id == "UCtest123"
        assert result.description == "Test channel description"
        assert result.country == "United States"

    def test_uses_input_url_when_channel_url_missing(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item(channelUrl=None)])
        result = get_channel_metadata("https://www.youtube.com/@missing")
        assert result.channel_url == "https://www.youtube.com/@missing"

    def test_missing_fields_default_to_empty(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"channelId": "UCabc"}])
        result = get_channel_metadata("https://www.youtube.com/@test")
        assert result.channel_name == ""
        assert result.channel_url == "https://www.youtube.com/@test"
        assert result.subscriber_count == 0
        assert result.total_videos == 0
        assert result.channel_id == "UCabc"
        assert result.description == ""
        assert result.country == ""

    def test_raises_on_empty_dataset(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [])
        try:
            get_channel_metadata("https://www.youtube.com/@test")
            assert False, "Expected ActorError"
        except ActorError:
            pass

    def test_raises_on_invalid_url(self, mock_apify_client):
        try:
            get_channel_metadata("not-a-url")
            assert False, "Expected ValueError"
        except ValueError:
            pass
