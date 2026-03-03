import os
import json
import requests
from config.logger import setup_logger

logger = setup_logger(__name__)


class LogForwarder:
    """Forwards webhook event data to a third-party logging service (Logtail / Better Stack)"""

    # Logtail ingestion endpoint
    LOGTAIL_ENDPOINT = "https://in.logs.betterstack.com"

    def __init__(self):
        """Initialize the log forwarder with the Logtail source token"""
        self.source_token = os.getenv("LOGTAIL_SOURCE_TOKEN")
        if not self.source_token:
            logger.warning(
                "LOGTAIL_SOURCE_TOKEN not configured – log forwarding is disabled"
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def forward(self, event_type: str, data: dict) -> bool:
        """
        Forward a webhook payload as a structured log entry.

        Args:
            event_type: SendCloud event name (e.g. 'deliver', 'open', …)
            data:       Raw webhook form data as a dict

        Returns:
            bool: True if the entry was accepted, False otherwise
        """
        if not self.source_token:
            logger.warning("Log forwarding skipped – LOGTAIL_SOURCE_TOKEN not set")
            return False

        payload = {
            "message": f"SendCloud webhook event: {event_type}",
            "event": event_type,
            "email": data.get("email"),
            "token": data.get("token"),
            "timestamp": data.get("timestamp"),
            "data": data,
        }

        return self._send(payload)

    def forward_raw(self, payload: dict) -> bool:
        """
        Forward an arbitrary dict as a structured log entry.

        Args:
            payload: Any JSON-serialisable dictionary

        Returns:
            bool: True if the entry was accepted, False otherwise
        """
        if not self.source_token:
            logger.warning("Log forwarding skipped – LOGTAIL_SOURCE_TOKEN not set")
            return False

        return self._send(payload)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _send(self, payload: dict) -> bool:
        """POST the payload to the Logtail HTTP source endpoint."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.source_token}",
        }
        try:
            response = requests.post(
                self.LOGTAIL_ENDPOINT,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False),
                timeout=5,
            )
            if response.status_code in (200, 202):
                logger.info(
                    f"Log forwarded to Logtail: event={payload.get('event', 'n/a')}"
                )
                return True
            else:
                logger.error(
                    f"Logtail rejected log entry: HTTP {response.status_code} – {response.text}"
                )
                return False
        except requests.exceptions.Timeout:
            logger.error("Logtail request timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to forward log to Logtail: {str(e)}")
            return False

