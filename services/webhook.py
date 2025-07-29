"""
Webhook service module for handling Telegram webhook requests.
Uses FastAPI for high-performance async webhook handling.
"""

import logging
from typing import Optional, Tuple
from fastapi import FastAPI, Request, HTTPException, Header
from telegram import Update
from telegram.ext import Application
from core.config import Config

logger = logging.getLogger(__name__)


class WebhookService:
    """FastAPI-based webhook service for Telegram bot."""
    
    def __init__(self, application: Application):
        self.application = application
        self.app = FastAPI(
            title="Telegram Bot Webhook",
            description="Webhook server for Telegram bot",
            version="1.0.0"
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up FastAPI routes."""
        
        @self.app.post("/webhook")
        async def webhook_handler(
            request: Request,
            x_telegram_bot_api_secret_token: Optional[str] = Header(None)
        ):
            """Handle incoming webhook requests from Telegram."""
            
            # Verify secret token if configured
            if Config.WEBHOOK_SECRET_TOKEN:
                if x_telegram_bot_api_secret_token != Config.WEBHOOK_SECRET_TOKEN:
                    logger.warning("Invalid secret token in webhook request")
                    raise HTTPException(status_code=403, detail="Invalid secret token")
            
            try:
                # Get request body
                body = await request.body()
                
                # Parse update
                update = Update.de_json(await request.json(), self.application.bot)
                
                if update:
                    # Process update
                    await self.application.process_update(update)
                    logger.debug(f"Processed webhook update: {update.update_id}")
                else:
                    logger.warning("Received invalid update from webhook")
                
                return {"status": "ok"}
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "bot_username": Config.BOT_USERNAME,
                "mode": "webhook"
            }
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "message": "Telegram Bot Webhook Server",
                "status": "running",
                "mode": "webhook"
            }
    
    async def setup_webhook(self):
        """Set up webhook with Telegram."""
        try:
            webhook_url = f"{Config.WEBHOOK_URL}/webhook"
            
            # Set webhook
            await self.application.bot.set_webhook(
                url=webhook_url,
                secret_token=Config.WEBHOOK_SECRET_TOKEN if Config.WEBHOOK_SECRET_TOKEN else None,
                drop_pending_updates=True
            )
            
            logger.info(f"Webhook set successfully: {webhook_url}")
            
            # Get webhook info
            webhook_info = await self.application.bot.get_webhook_info()
            logger.info(f"Webhook info: {webhook_info}")
            
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            raise
    
    async def remove_webhook(self):
        """Remove webhook from Telegram."""
        try:
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook removed successfully")
        except Exception as e:
            logger.error(f"Failed to remove webhook: {e}")
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application."""
        return self.app


def create_webhook_service(application: Application) -> Tuple[FastAPI, WebhookService]:
    """Create and configure webhook service."""
    webhook_service = WebhookService(application)
    return webhook_service.get_app(), webhook_service