import logging

class ColorFormatter(logging.Formatter):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    NAME = "\033[35m"
    LEVEL = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m\033[97m",
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL.get(record.levelno, "")
        record.levelname = f"{self.BOLD}{level_color}{record.levelname}{self.RESET}"
        record.name = f"{self.BOLD}{self.NAME}{record.name}{self.RESET}"
        return super().format(record)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = ColorFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
