from dataclasses import dataclass, field
import requests


from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class TelegramChatAction(BufferNode, Action):
    
    token : str = field(default=None, metadata={"description": "telegram bot token"})
    chat_id : str = field(default=None, metadata={"description": "id of the chat to use"})