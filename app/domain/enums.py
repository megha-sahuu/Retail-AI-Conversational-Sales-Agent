from enum import Enum


class Channel(str, Enum):
    WEB_CHAT = "web_chat"
    KIOSK = "kiosk"
    WHATSAPP = "whatsapp"
    MOBILE_APP = "mobile_app"
    VOICE = "voice"
