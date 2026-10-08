"""Run the full ETL pipeline: extract -> transform -> load."""
import logging
import time

import extract
import load
import transform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run each ETL step in order and stop if one of them fails."""
    steps = [
        ("Extract", extract.main),
        ("Transform", transform.main),
        ("Load", load.main),
    ]

    start = time.perf_counter()
    for name, step in steps:
        logger.info("Starting %s step", name)
        try:
            step()
        except Exception:
            logger.exception("%s step failed. Pipeline stopped.", name)
            raise SystemExit(1)
        logger.info("Finished %s step", name)

    elapsed = time.perf_counter() - start
    logger.info("Pipeline completed successfully in %.1f seconds", elapsed)


if __name__ == "__main__":
    run_pipeline()