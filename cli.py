"""Command-line interface for the Telegram bot."""

import argparse
import asyncio
import sys
from core.runner import run_bot
from core.logger import setup_logging

logger = setup_logging()


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Telegram Bot Template CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                    # Run with default mode from config
  python cli.py --mode polling     # Run in polling mode
  python cli.py --mode webhook     # Run in webhook mode
  python cli.py -m polling         # Short form
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["polling", "webhook"],
        help="Bot mode to run (overrides config setting)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Telegram Bot Template 1.0.0"
    )
    
    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        logger.info("Starting Telegram Bot Template...")
        asyncio.run(run_bot(args.mode))
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()