import logging

class ColourFormatter(logging.Formatter):
    """Logging formatter with level-specific colours."""

    COLOURS = {
        logging.DEBUG: "\033[1;34m",   # Blue
        logging.INFO: "\033[1;32m",    # Green
        logging.WARNING: "\033[1;33m", # Yellow
        logging.ERROR: "\033[1;31m",   # Red
        logging.CRITICAL: "\033[1;41m" # Red background
    }

    RESET = "\033[0m"

    def format(self, record):
        colour = self.COLOURS.get(record.levelno, self.RESET)
        fmt = (
            f"\033[1;37m[%(asctime)s]\033[0m "
            f"{colour}%(levelname)-8s{self.RESET} "
            f"\033[1;33m%(name)s\033[0m: "
            "%(message)s"
        )
        formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(level=logging.INFO):
    """Set up a nicer logging format for the application."""
    handler = logging.StreamHandler()
    handler.setFormatter(ColourFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

