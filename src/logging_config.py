"""Detailed logging setup shared across the app for easier debugging."""
import logging
import sys

_CONFIGURED = False


def setup_logging(level: int = logging.DEBUG) -> None:
    """Configure the root logger once with a verbose, timestamped format."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # Third-party libraries are noisy at DEBUG; keep them at INFO.
    for noisy in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.INFO)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
