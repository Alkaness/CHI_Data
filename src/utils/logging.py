import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure a simple, application-wide logging format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
