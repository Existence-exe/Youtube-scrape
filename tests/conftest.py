from unittest.mock import MagicMock, patch

import pytest


def mock_run(dataset_id: str = "ds-123") -> MagicMock:
    run = MagicMock()
    run.default_dataset_id = dataset_id
    return run


def mock_actor_call(mock_client: MagicMock, items: list[dict], dataset_id: str = "ds-123") -> None:
    mock_actor = MagicMock()
    mock_actor.call.return_value = mock_run(dataset_id)
    mock_client.actor.return_value = mock_actor
    mock_dataset = MagicMock()
    mock_dataset.iterate_items.return_value = iter(items)
    mock_client.dataset.return_value = mock_dataset


@pytest.fixture
def mock_apify_client():
    patcher = patch("src.client._client")
    mock_client = patcher.start()
    yield mock_client
    patcher.stop()
