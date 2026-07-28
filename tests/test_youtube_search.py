from src.client import ActorError
from src.youtube_search import search_videos
from tests.conftest import mock_actor_call


def _item(**overrides):
    defaults = {
        "title": "Search Result",
        "channelName": "Test Channel",
        "url": "https://www.youtube.com/watch?v=abc123",
        "viewCount": 5000,
        "duration": "00:05:00",
        "thumbnailUrl": "https://i.ytimg.com/vi/abc123/default.jpg",
    }
    defaults.update(overrides)
    return defaults


class TestSearchVideos:
    def test_returns_all_fields(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [_item()])
        results = search_videos("test query")
        assert len(results) == 1
        r = results[0]
        assert r.title == "Search Result"
        assert r.channel_name == "Test Channel"
        assert r.video_url == "https://www.youtube.com/watch?v=abc123"
        assert r.view_count == 5000
        assert r.duration == "00:05:00"
        assert r.thumbnail_url == "https://i.ytimg.com/vi/abc123/default.jpg"

    def test_returns_list_of_results(self, mock_apify_client):
        items = [_item(), _item(title="Second", viewCount=3000)]
        mock_actor_call(mock_apify_client, items)
        results = search_videos("test query")
        assert len(results) == 2
        assert results[0].title == "Search Result"
        assert results[1].title == "Second"
        assert results[1].view_count == 3000

    def test_returns_empty_list_when_no_results(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [])
        results = search_videos("empty query")
        assert results == []

    def test_missing_fields_default_to_empty(self, mock_apify_client):
        mock_actor_call(mock_apify_client, [{"title": "Minimal"}])
        results = search_videos("test")
        assert len(results) == 1
        r = results[0]
        assert r.title == "Minimal"
        assert r.channel_name == ""
        assert r.video_url == ""
        assert r.view_count == 0
        assert r.duration == ""
        assert r.thumbnail_url == ""

    def test_raises_on_empty_query(self, mock_apify_client):
        try:
            search_videos("")
            assert False, "Expected ValueError"
        except ValueError:
            pass
