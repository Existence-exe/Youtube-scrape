# YouTube Analyzer

A CLI tool for fetching and analyzing YouTube video data using [Apify Actors](https://apify.com/actors).

## Features

- **Search YouTube** — Search videos by keyword and select one for analysis
- **Video Metadata** — Title, description, upload date, view count, duration, tags, thumbnails
- **Channel Metadata** — Channel name, subscriber count, total videos, country, description
- **Shorts Analysis** — Total shorts, average views, most-viewed short, first upload year
- **Reports** — Save complete analytics as JSON (nested) and CSV (flattened)
- **Retry Logic** — Exponential backoff on Apify API failures (3 retries)
- **Logging** — Console + file logging to `logs/analytics.log`

## Installation

```bash
git clone <repo-url>
cd youtube-analyzer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy the environment file and add your Apify API token:

```bash
cp .env.example .env
```

### Environment Variables

| Variable       | Required | Default  | Description                     |
|---------------|----------|----------|---------------------------------|
| `APIFY_TOKEN` | Yes      | —        | Your Apify API authentication token |
| `OUTPUT_DIR`  | No       | `output` | Directory for JSON/CSV reports  |

Get your Apify API token at [console.apify.com](https://console.apify.com/).

## Usage

```bash
source .venv/bin/activate
python -m src.main
```

The CLI guides you through the workflow:

1. **Search** — Enter a keyword to find YouTube videos
2. **Select** — Choose a result from the numbered table
3. **Analyze** — The tool fetches video metadata, channel metadata, and shorts statistics
4. **Report** — A formatted analytics report is displayed and saved to `output/report.json` and `output/report.csv`

### Output

```
output/
  report.json    # Complete nested report (video, channel, shorts)
  report.csv     # Flattened single-row report
logs/
  analytics.log  # Execution logs
```

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## Project Architecture

```
src/
  __init__.py
  config.py        # Environment, logging, constants
  client.py        # ApifyClient wrapper, retry logic, ActorError
  models.py        # Dataclasses: VideoMetadata, ChannelMetadata, ShortInfo, etc.
  youtube_search.py  # search_videos(query) → list[SearchResult]
  video.py         # get_video_metadata(url), get_first_upload_year(url)
  channel.py       # get_channel_metadata(url) → ChannelMetadata
  shorts.py        # get_channel_shorts(url) → list[ShortInfo]
  statistics.py    # Shorts analytics functions
  report.py        # generate_report(), save_report()
  main.py          # CLI entry point
  utils.py         # (reserved)
tests/
  conftest.py      # Shared fixtures and mock helpers
  test_client.py
  test_channel.py
  test_report.py
  test_shorts.py
  test_statistics.py
  test_video.py
  test_youtube_search.py
```

### Data Flow

```
User Input → search_videos() → numbered results → user selects
    ↓
get_video_metadata() → VideoMetadata dataclass
    ↓
get_channel_metadata() → ChannelMetadata dataclass
    ↓
get_channel_shorts() + get_first_upload_year() → ShortsStatistics
    ↓
generate_report() → AnalyticsReport → output/report.json + output/report.csv
```

### Apify Actors Used

| Actor | ID |
|-------|-----|
| YouTube Scraper | `h7sDV53CddomktSi5` |
| Fast YouTube Channel Scraper | `67Q6fmd8iedTVcCwY` |
| YouTube Shorts Scraper | `65aDXHapxlrOSbbUP` |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `APIFY_TOKEN not set` | Create `.env` file with your token from console.apify.com |
| `Apify API error` | Check your token is valid and has billing enabled |
| `No data returned` | The video may be private, deleted, or the URL is invalid |
| `Actor failed` | Check logs/analytics.log for details; retries happen automatically |
| Module not found | Run `pip install -r requirements.txt` in your virtual environment |
