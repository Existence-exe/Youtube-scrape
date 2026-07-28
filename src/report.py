import csv
import json
import os
from typing import Any

from src.config import OUTPUT_DIR
from src.models import AnalyticsReport, ChannelMetadata, ShortsStatistics, VideoMetadata
from src import storage  # new import (ensure src is a package or adjust import as needed)


_REPORT_CSV_COLUMNS = [
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


def _json_value(v: Any) -> Any:
    if isinstance(v, dict):
        return json.dumps(v)
    if isinstance(v, list):
        if v and isinstance(v[0], dict):
            return v
        return ", ".join(str(x) for x in v)
    return v


def _csv_value(v: Any) -> str:
    if isinstance(v, (str, int, float)):
        return str(v)
    if isinstance(v, dict):
        return json.dumps(v)
    if isinstance(v, list):
        if v and isinstance(v[0], dict):
            return json.dumps(v)
        return ", ".join(str(x) for x in v)
    return str(v)


def _expand_rows(data: dict[str, Any]) -> list[dict[str, str]]:
    list_keys = {
        k: v
        for k, v in data.items()
        if isinstance(v, list) and v and isinstance(v[0], dict)
    }
    if not list_keys:
        return [{k: _csv_value(v) for k, v in data.items()}]
    scalar = {k: _csv_value(v) for k, v in data.items() if k not in list_keys}
    rows = []
    max_len = max(len(v) for v in list_keys.values())
    for i in range(max_len):
        row = dict(scalar)
        for k, lst in list_keys.items():
            if i < len(lst):
                item = lst[i]
                if isinstance(item, dict):
                    for sub_k, sub_v in item.items():
                        row[f"{k}_{sub_k}"] = _csv_value(sub_v)
                else:
                    row[k] = _csv_value(item)
            else:
                for sub_k in lst[0]:
                    row[f"{k}_{sub_k}"] = ""
        rows.append(row)
    return rows


def save_report(data: dict[str, Any], filename: str = "report") -> tuple[str, str]:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, f"{filename}.json")
    csv_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    with open(json_path, "w") as f:
        json_data = {k: _json_value(v) for k, v in data.items()}
        json.dump(json_data, f, indent=2)
    with open(csv_path, "w", newline="") as f:
        rows = _expand_rows(data)
        if rows:
            headers = list(rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
    return json_path, csv_path


def generate_report(
    video: VideoMetadata,
    channel: ChannelMetadata,
    shorts: ShortsStatistics,
) -> AnalyticsReport:
    report = AnalyticsReport(video=video, channel=channel, shorts=shorts)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    json_path = os.path.join(OUTPUT_DIR, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(OUTPUT_DIR, "report.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_REPORT_CSV_COLUMNS)
        writer.writerow([
            video.title,
            video.channel_name,
            channel.subscriber_count,
            video.view_count,
            video.duration,
            shorts.average_views,
            shorts.total_shorts,
            shorts.first_upload_year,
            video.video_url,
        ])

    # persist to repo database history file
    try:
        db_path = storage.append_analysis(report.to_dict())
    except Exception:
        # do not fail the analysis if history append fails, but log it for debugging
        db_path = None

    return report
