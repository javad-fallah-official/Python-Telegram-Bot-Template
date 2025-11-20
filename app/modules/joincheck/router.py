from aiogram import Router, F
from .handlers import verify_sponsor_join
from .middleware import JoinCheckMiddleware

router = Router()
router.callback_query.register(verify_sponsor_join, F.data == "verify_sponsor_join")
