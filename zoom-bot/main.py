#!/usr/bin/env python3

import os
import logging
from src.config import DEBUG, DEBUG_PATH
from src.scheduler import MeetingScheduler

def main():
    """Основная функция приложения"""
    
    # Создаем директорию для отладочных скриншотов
    if DEBUG:
        try:
            os.makedirs(DEBUG_PATH, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create screenshot folder: {str(e)}")
            raise
            
    # Создаем и запускаем планировщик
    scheduler = MeetingScheduler()
    scheduler.run()

if __name__ == '__main__':
    main() 