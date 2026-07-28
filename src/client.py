import logging
import time
from typing import Any

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError

from src.config import APIFY_TOKEN

logger = logging.getLogger(__name__)

_client = ApifyClient(token=APIFY_TOKEN)

_MAX_RETRIES = 3
_BASE_DELAY_S = 1.0


class ActorError(RuntimeError):
    """Raised when an Apify actor fails after all retries."""


def test_connection() -> dict[str, Any]:
    try:
        user_info = _client.user().get()
    except ApifyApiError as e:
        return {"error": f"Apify API error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

    if user_info is None:
        return {"error": "User not found"}

    result: dict[str, Any] = {"username": user_info.username}
    for attr in ("email", "id"):
        try:
            val = getattr(user_info, attr)
            if val is not None:
                key = "account_id" if attr == "id" else attr
                result[key] = val
        except AttributeError:
            pass
    return result


def run_actor(
    actor_id: str,
    run_input: dict[str, Any],
    retries: int = _MAX_RETRIES,
) -> list[dict[str, Any]]:
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                "Calling actor %s (attempt %d/%d)",
                actor_id,
                attempt,
                retries,
            )
            run = _client.actor(actor_id).call(run_input=run_input)
        except ApifyApiError as e:
            last_error = e
            logger.warning(
                "Apify API error on attempt %d/%d: %s",
                attempt,
                retries,
                e,
            )
            if attempt < retries:
                delay = _BASE_DELAY_S * (2 ** (attempt - 1))
                logger.info("Retrying in %.1f seconds...", delay)
                time.sleep(delay)
            continue
        except Exception as e:
            logger.error(
                "Unexpected error on attempt %d/%d: %s",
                attempt,
                retries,
                e,
            )
            raise ActorError(f"Unexpected error: {e}") from e

        dataset_id = run.default_dataset_id
        try:
            items = list(_client.dataset(dataset_id).iterate_items())
        except Exception as e:
            logger.error("Failed to iterate dataset %s: %s", dataset_id, e)
            raise ActorError(f"Failed to read actor output: {e}") from e

        logger.info("Actor %s returned %d items in %.1fs", actor_id, len(items), 0)
        return items

    raise ActorError(
        f"Apify API error after {retries} retries: {last_error}"
    ) from last_error
