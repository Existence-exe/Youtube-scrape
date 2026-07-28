from unittest.mock import MagicMock

import pytest

from src.client import ActorError, run_actor
from src.client import test_connection as get_user_info
from tests.conftest import mock_actor_call, mock_run


def _make_apify_error(status_code: int = 500):
    from apify_client.errors import ApifyApiError
    response = MagicMock()
    response.status_code = status_code
    return ApifyApiError(response, 1)


class TestRunActor:
    def test_returns_items_on_success(self, mock_apify_client):
        items = [{"id": "abc"}, {"id": "def"}]
        mock_actor_call(mock_apify_client, items)
        result = run_actor("actor-id", {"key": "val"})
        assert result == items

    def test_retries_on_apify_error_then_succeeds(self, mock_apify_client):
        mock_actor = MagicMock()
        mock_actor.call.side_effect = [_make_apify_error(), _make_apify_error(), mock_run()]
        mock_apify_client.actor.return_value = mock_actor
        mock_dataset = MagicMock()
        mock_dataset.iterate_items.return_value = iter([{"id": "ok"}])
        mock_apify_client.dataset.return_value = mock_dataset

        result = run_actor("actor-id", {"key": "val"}, retries=3)
        assert result == [{"id": "ok"}]
        assert mock_actor.call.call_count == 3

    def test_raises_after_all_retries_exhausted(self, mock_apify_client):
        mock_actor = MagicMock()
        mock_actor.call.side_effect = [_make_apify_error(), _make_apify_error(), _make_apify_error()]
        mock_apify_client.actor.return_value = mock_actor

        with pytest.raises(ActorError, match="Apify API error after 3 retries"):
            run_actor("actor-id", {"key": "val"}, retries=3)


class TestConnection:
    def test_returns_username_on_success(self, mock_apify_client):
        user = MagicMock()
        user.username = "testuser"
        user.email = "test@example.com"
        user.id = "user123"
        mock_apify_client.user.return_value.get.return_value = user

        result = get_user_info()
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["account_id"] == "user123"

    def test_handles_public_user_info(self, mock_apify_client):
        user = MagicMock()
        user.username = "publicuser"
        del user.email
        del user.id
        mock_apify_client.user.return_value.get.return_value = user

        result = get_user_info()
        assert result["username"] == "publicuser"

    def test_returns_error_on_none_user(self, mock_apify_client):
        mock_apify_client.user.return_value.get.return_value = None
        result = get_user_info()
        assert "error" in result
