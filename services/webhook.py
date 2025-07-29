"""Webhook service module for handling Telegram webhook requests."""

import logging
import uvicorn
from typing import Optional, Tuple
from fastapi import FastAPI, Request, HTTPException, Header
from telegram import Update
from telegram.ext import Application
from core.config import Config
from .base import BotService

logger = logging.getLogger(__name__)


class WebhookService(BotService):
    """FastAPI-based webhook service for Telegram bot."""
    
    def __init__(self, application: Application):
        super().__init__(application)
        self.app = FastAPI(
            title="Telegram Bot Webhook",
            description="Webhook server for Telegram bot",
            version="1.0.0"
        )
        self.server = None
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up FastAPI routes."""
        
        @self.app.post("/webhook")
        async def webhook_handler(
            request: Request,
            x_telegram_bot_api_secret_token: Optional[str] = Header(None)
        ):
            """Handle incoming webhook requests from Telegram."""
            
            if Config.WEBHOOK_SECRET_TOKEN:
                if x_telegram_bot_api_secret_token != Config.WEBHOOK_SECRET_TOKEN:
                    logger.warning("Invalid secret token in webhook request")
                    raise HTTPException(status_code=403, detail="Invalid secret token")
            
            try:
                update = Update.de_json(await request.json(), self.application.bot)
                
                if update:
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
    
    async def setup(self) -> None:
        """Set up webhook with Telegram."""
        try:
            webhook_url = f"{Config.WEBHOOK_URL}/webhook"
            
            await self.application.bot.set_webhook(
                url=webhook_url,
                secret_token=Config.WEBHOOK_SECRET_TOKEN if Config.WEBHOOK_SECRET_TOKEN else None,
                drop_pending_updates=True
            )
            
            logger.info(f"Webhook set successfully: {webhook_url}")
            
            webhook_info = await self.application.bot.get_webhook_info()
            logger.info(f"Webhook info: {webhook_info}")
            
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            raise
    
    async def start(self) -> None:
        """Start the webhook service."""
        logger.info("Starting webhook service...")
        
        try:
            await self.application.start()
            await self.setup()
            
            config = uvicorn.Config(
                self.app,
                host=Config.WEBHOOK_HOST,
                port=Config.WEBHOOK_PORT,
                log_level="info" if Config.DEBUG else "warning",
                access_log=Config.DEBUG
            )
            
            self.server = uvicorn.Server(config)
            self._running = True
            
            logger.info(f"Starting webhook server on {Config.WEBHOOK_HOST}:{Config.WEBHOOK_PORT}")
            await self.server.serve()
            
        except Exception as e:
            logger.error(f"Error in webhook service: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the webhook service."""
        if not self._running:
            return
            
        logger.info("Stopping webhook service...")
        self._running = False
        
        try:
            await self.cleanup()
            await self.application.stop()
            logger.info("Webhook service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping webhook service: {e}")
    
    async def cleanup(self) -> None:
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