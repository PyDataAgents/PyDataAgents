from dataclasses import dataclass, field

from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes

from ...agents.Agent import Agent
from ..BufferNode import BufferNode
from .ObserverTriggerAction import ObserverTriggerAction


@dataclass
class TelegramTriggerAction(BufferNode, ObserverTriggerAction):
    
    token : str = field(default=None, metadata={"description": "telegram bot token"})
    allowed_user_ids : list[str] = field(default_factory=list, metadata={"description": "list of allowed user ids in the chat"})
    
    def __post_init__(self):
        super().__post_init__()
        self._telegram_app : Application = None
    
    def _on_install(self, agent : Agent = None):
        BufferNode._on_install(self, agent)
        ObserverTriggerAction._on_install(self, agent)
    
    async def _start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bot is running 🚀")
        
    def start_trigger(self):
        self._telegram_app = ApplicationBuilder().token(self.token).build()
        self._telegram_app.add_handler(CommandHandler("start", self._start_cmd))