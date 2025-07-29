"""
Keyboard building utilities.
"""

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardBuilder:
    """Utility class for building inline keyboards."""
    
    @staticmethod
    def build_menu(
        buttons: List[InlineKeyboardButton],
        n_cols: int = 1,
        header_buttons: List[InlineKeyboardButton] = None,
        footer_buttons: List[InlineKeyboardButton] = None
    ) -> InlineKeyboardMarkup:
        """Build inline keyboard menu."""
        menu = []
        
        # Add header buttons
        if header_buttons:
            for button in header_buttons:
                menu.append([button])
        
        # Add main buttons in rows
        for i in range(0, len(buttons), n_cols):
            menu.append(buttons[i:i + n_cols])
        
        # Add footer buttons
        if footer_buttons:
            for button in footer_buttons:
                menu.append([button])
        
        return InlineKeyboardMarkup(menu)
    
    @staticmethod
    def pagination_keyboard(
        current_page: int,
        total_pages: int,
        callback_prefix: str = "page"
    ) -> InlineKeyboardMarkup:
        """Build pagination keyboard."""
        buttons = []
        
        # Previous button
        if current_page > 1:
            buttons.append(
                InlineKeyboardButton("◀️ Previous", callback_data=f"{callback_prefix}_{current_page - 1}")
            )
        
        # Page info
        buttons.append(
            InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
        )
        
        # Next button
        if current_page < total_pages:
            buttons.append(
                InlineKeyboardButton("Next ▶️", callback_data=f"{callback_prefix}_{current_page + 1}")
            )
        
        return InlineKeyboardMarkup([buttons])