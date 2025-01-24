import logging
import time
import requests
from typing import Optional
from src.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_RETRIES

class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram"""
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or TELEGRAM_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self._validate_credentials()
        
    def _validate_credentials(self) -> None:
        """Проверяет валидность учетных данных Telegram"""
        if not self.token or len(self.token) < 3:
            logging.error("Telegram token is missing or invalid")
            self.token = None
            
        if not self.chat_id or len(self.chat_id) < 3:
            logging.error("Telegram chat_id is missing or invalid")
            self.chat_id = None
            
    def send_message(self, text: str) -> bool:
        """
        Отправляет сообщение в Telegram
        
        Args:
            text: Текст сообщения
            
        Returns:
            True если сообщение отправлено успешно, False в противном случае
        """
        if not self.token or not self.chat_id:
            logging.error("Telegram credentials are not configured")
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            "chat_id": self.chat_id,
            "text": text
        }
        
        for attempt in range(TELEGRAM_RETRIES):
            try:
                response = requests.get(url, params=params)
                result = response.json()
                
                if result.get('ok'):
                    return True
                    
                logging.error(f"Telegram API error: {result}")
                
            except Exception as e:
                logging.error(f"Failed to send Telegram message: {str(e)}")
                
            if attempt < TELEGRAM_RETRIES - 1:
                logging.error(f"Retrying in 5 seconds... (attempt {attempt + 1}/{TELEGRAM_RETRIES})")
                time.sleep(5)
                
        return False

# Создаем глобальный экземпляр для использования во всем приложении
notifier = TelegramNotifier() 