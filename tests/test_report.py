import csv as csv_module
import json
import os

import pytest

from src.models import ChannelMetadata, ShortsStatistics, VideoMetadata
from src.report import generate_report, save_report


@pytest.fixture(autouse=True)
def _output_dir(monkeypatch, tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    monkeypatch.setattr("src.report.OUTPUT_DIR", str(d))
    return d


class TestSaveReport:
    def test_saves_json_and_csv(self, _output_dir):
        json_path, csv_path = save_report({"title": "hello"})
        assert os.path.exists(json_path)
        assert os.path.exists(csv_path)
        data = json.loads(open(json_path).read())
        assert data["title"] == "hello"

    def test_empty_dict(self, _output_dir):
        save_report({})
        data = json.loads(open(os.path.join(_output_dir, "report.json")).read())
        assert data == {}


class TestGenerateReport:
    def _make_models(self):
        return (
            VideoMetadata(
                title="My Video",
                channel_name="My Channel",
                channel_url="https://youtube.com/@channel",
                view_count=5000,
                duration="10:30",
                video_url="https://youtube.com/watch?v=abc",
                video_id="abc123",
                description="A test",
                upload_date="2023-01-01",
                thumbnail_url="https://i.ytimg.com/vi/abc/default.jpg",
                tags=["tag1"],
            ),
            ChannelMetadata(
                channel_name="My Channel",
                channel_url="https://youtube.com/@channel",
                subscriber_count=10000,
                channel_id="UCabc",
                country="US",
                description="Channel desc",
                total_videos=50,
            ),
            ShortsStatistics(
                average_views=250.5,
                total_shorts=20,
                first_upload_year="2019",
            ),
        )

    def test_returns_analytics_report(self, _output_dir):
        video, channel, shorts = self._make_models()
        result = generate_report(video, channel, shorts)
        assert result.video == video
        assert result.channel == channel
        assert result.shorts == shorts

    def test_json_has_nested_structure(self, _output_dir):
        video, channel, shorts = self._make_models()
        generate_report(video, channel, shorts)
        with open(os.path.join(_output_dir, "report.json")) as f:
            got = json.load(f)
        assert got["video"]["title"] == "My Video"
        assert got["channel"]["subscriber_count"] == 10000
        assert got["shorts"]["average_views"] == 250.5

    def test_csv_has_correct_columns(self, _output_dir):
        video, channel, shorts = self._make_models()
        generate_report(video, channel, shorts)
        with open(os.path.join(_output_dir, "report.csv"), newline="") as f:
            header = next(csv_module.reader(f))
        assert header == [
            "Video Title",
            "Channel",
            "Subscribers",
            "Views",
            "Duration",
            "Average Shorts Views",
            "Total Shorts",
            "First Upload Year",
            "Video URL",
        ]

    def test_csv_values_match_input(self, _output_dir):
        video = VideoMetadata(title="V", channel_name="C", view_count=100, duration="5:00", video_url="http://x")
        channel = ChannelMetadata(subscriber_count=500)
        shorts = ShortsStatistics(average_views=50.5, total_shorts=10, first_upload_year="2020")
        generate_report(video, channel, shorts)
        with open(os.path.join(_output_dir, "report.csv"), newline="") as f:
            rows = list(csv_module.reader(f))
        assert rows[1] == ["V", "C", "500", "100", "5:00", "50.5", "10", "2020", "http://x"]

    def test_csv_handles_missing_fields(self, _output_dir):
        video = VideoMetadata(title="Only Title")
        channel = ChannelMetadata()
        shorts = ShortsStatistics()
        generate_report(video, channel, shorts)
        with open(os.path.join(_output_dir, "report.csv"), newline="") as f:
            rows = list(csv_module.reader(f))
        assert rows[1] == ["Only Title", "", "0", "0", "", "0.0", "0", "", ""]
