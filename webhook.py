"""Entry point for running the bot in webhook mode."""

from core.runner import run_bot
import asyncio
import sys
from core.logger import setup_logging

logger = setup_logging()


def main() -> None:
    """Main entry point for webhook mode."""
    try:
        asyncio.run(run_bot("webhook"))
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start bot in webhook mode: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()