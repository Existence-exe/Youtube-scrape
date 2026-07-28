from src.client import ActorError
from src.video import get_first_upload_year, get_video_metadata
from tests.conftest import mock_actor_call


def _item(**overrides):
    defaults = {
        "id": "dQw4w9WgXcQ",
        "title": "Test Video",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "channelName": "Test Channel",
        "channelUrl": "https://www.youtube.com/@testchannel",
        "viewCount": 1000,
        "date": "2024-01-15T12:00:00.000Z",
        "duration": "00:03:30",
        "thumbnailUrl": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
        "description": "A test video description",
        "hashtags": ["#test", "#demo"],
        "text": "",
    }
    defaults.update(overrides)
    return defaults


class TestGetVideoMetadata:
    def test_returns_all_fields(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item()])
        result = get_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result.title == "Test Video"
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result.channel_name == "Test Channel"
        assert result.channel_url == "https://www.youtube.com/@testchannel"
        assert result.view_count == 1000
        assert result.upload_date == "2024-01-15T12:00:00.000Z"
        assert result.duration == "00:03:30"
        assert result.thumbnail_url == "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg"
        assert result.description == "A test video description"
        assert result.tags == ["#test", "#demo"]

    def test_missing_fields_default_to_empty(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"id": "abc123", "title": "Minimal"}])
        result = get_video_metadata("https://www.youtube.com/watch?v=abc123")
        assert result.title == "Minimal"
        assert result.channel_name == ""
        assert result.view_count == 0
        assert result.upload_date == ""
        assert result.duration == ""
        assert result.thumbnail_url == ""
        assert result.tags == []

    def test_tags_from_hashtags_list(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item(hashtags=["#a", "#b"])])
        result = get_video_metadata("https://www.youtube.com/watch?v=test")
        assert result.tags == ["#a", "#b"]

    def test_tags_from_hashtags_string(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item(hashtags="#single")])
        result = get_video_metadata("https://www.youtube.com/watch?v=test")
        assert result.tags == ["#single"]

    def test_tags_from_text(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item(hashtags=None, text="Check out #fun and #games here!")])
        result = get_video_metadata("https://www.youtube.com/watch?v=test")
        assert result.tags == ["#fun", "#games"]

    def test_no_tags_when_missing(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item(hashtags=None, text="No tags here")])
        result = get_video_metadata("https://www.youtube.com/watch?v=test")
        assert result.tags == []

    def test_raises_on_empty_dataset(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [])
        try:
            get_video_metadata("https://www.youtube.com/watch?v=test")
            assert False, "Expected ActorError"
        except ActorError:
            pass

    def test_raises_on_missing_title(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"id": "abc"}])
        try:
            get_video_metadata("https://www.youtube.com/watch?v=test")
            assert False, "Expected ActorError"
        except ActorError:
            pass

    def test_raises_on_invalid_url(self, mock_apify_client):
        try:
            get_video_metadata("not-a-url")
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestGetFirstUploadYear:
    def test_returns_year_from_date(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"date": "2020-06-15T10:00:00.000Z"}])
        result = get_first_upload_year("https://www.youtube.com/@channel")
        assert result == "2020"

    def test_returns_empty_when_no_items(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [])
        result = get_first_upload_year("https://www.youtube.com/@channel")
        assert result == ""

    def test_returns_empty_when_no_date(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"title": "No Date"}])
        result = get_first_upload_year("https://www.youtube.com/@channel")
        assert result == ""

    def test_returns_empty_on_actor_error(self, mock_apify_client):
        mock_apify_client.actor.return_value.call.side_effect = Exception("API error")
        result = get_first_upload_year("https://www.youtube.com/@channel")
        assert result == ""
