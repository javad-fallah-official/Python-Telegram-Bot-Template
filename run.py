#!/usr/bin/env python3
"""
Main entry point for the Telegram Bot Template.
This file provides a clean interface for running the bot in different modes.
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import main

if __name__ == "__main__":
    """
    Run the Telegram bot.
    
    The bot mode (polling/webhook) is determined by environment variables.
    See .env.example for configuration options.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)