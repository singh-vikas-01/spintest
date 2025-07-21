import time
import json
from spintest.validator import input_validator_e2e_task

from spintest import logger


class E2ETask:
    """E2E Task handler."""

    def __init__(self, url: str, task: dict):
        """Initialization of `E2ETask` class."""
        self.url = url
        self.task = task
        self.name = task.get("name")
        self.target = task.get("target")
        self.ignore = self.task.get("ignore", False)
        self.response = None

    def _response(self, status: str, task: str, message: str) -> dict:
        """Return the response with logging."""
        result = {
            "name": self.name,
            "status": status,
            "timestamp": time.asctime(),
            "duration_sec": self.task.get("duration_sec", None),
            "url": self.url,
            "task": task,
            "ignore": self.ignore,
            "message": message,
        }

        log_level = {"SUCCESS": logger.info, "FAILURE": logger.error}
        log_level.get(status, logger.critical)(json.dumps(result, indent=4))

        return result

    async def run(self) -> dict:
        """Run the E2E task."""
        # Input validation
        try:
            input_validator_e2e_task(self.task)
        except ValueError as e:
            logger.error(f"Validation error for E2ETask '{self.name}': {e}")
            return self._response(
                "FAILURE",
                "unknown",
                f"Task '{self.name}' schema validation failed: {str(e)}",
            )

        logger.info(f"Running E2ETask: {self.name}")
        start_time = time.monotonic()

        try:
            await self.target(url=self.url)
            self.task["duration_sec"] = round(time.monotonic() - start_time, 2)
            return self._response(
                "SUCCESS", self.target.__name__, "Task executed successfully."
            )
        except AssertionError as e:
            self.task["duration_sec"] = round(time.monotonic() - start_time, 2)
            logger.error(f"Assertion error in target for E2ETask '{self.name}': {e}")
            return self._response(
                "FAILURE",
                self.target.__name__,
                f"Task '{self.name}' failed due to assertion error: {str(e)}",
            )
        except Exception as e:
            self.task["duration_sec"] = round(time.monotonic() - start_time, 2)
            logger.error(f"Error executing target for E2ETask '{self.name}': {e}")
            return self._response(
                "ERROR",
                self.target.__name__,
                f"Task '{self.name}' encountered an error: {str(e)}",
            )
