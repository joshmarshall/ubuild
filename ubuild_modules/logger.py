import logging
import sys


FORMATTER = logging.Formatter(
    "%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(FORMATTER)
HANDLER.setLevel(logging.INFO)

LOGGER = logging.getLogger("ubuild")
LOGGER.addHandler(HANDLER)
