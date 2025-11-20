"""
File handling utilities.
"""

import logging
import aiohttp
import os

logger = logging.getLogger(__name__)


class FileHandler:
    """Utility class for handling files."""
    
    @staticmethod
    async def download_file(url: str, filename: str) -> bool:
        """Download file from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(filename, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return False
    
    @staticmethod
    def get_file_size(filename: str) -> int:
        """Get file size in bytes."""
        try:
            import os
            return os.path.getsize(filename)
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size to human readable format."""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"


# Standalone functions for easier usage
def ensure_directory(directory_path: str) -> bool:
    """Ensure directory exists, create if it doesn't."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1]