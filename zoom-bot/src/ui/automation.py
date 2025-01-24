import os
import time
import logging
import pyautogui
from typing import Optional, Tuple
from pathlib import Path
from src.config import IMG_PATH, DEBUG, DEBUG_PATH

class UIAutomation:
    """Класс для автоматизации UI действий"""
    
    def __init__(self):
        # Отключаем failsafe
        pyautogui.FAILSAFE = False
        
    def find_and_click(
        self,
        image_name: str,
        confidence: float = 0.9,
        min_search_time: int = 2,
        description: Optional[str] = None
    ) -> bool:
        """
        Находит изображение на экране и кликает по нему
        
        Args:
            image_name: Имя файла изображения
            confidence: Уровень уверенности при поиске
            min_search_time: Минимальное время поиска
            description: Описание действия для логирования
            
        Returns:
            True если успешно, False в противном случае
        """
        try:
            image_path = os.path.join(IMG_PATH, image_name)
            location = pyautogui.locateCenterOnScreen(
                image_path,
                confidence=confidence,
                minSearchTime=min_search_time
            )
            
            if location:
                pyautogui.click(location.x, location.y)
                if description:
                    logging.info(f"Successfully clicked {description}")
                return True
                
        except Exception as e:
            if description:
                logging.error(f"Failed to click {description}: {str(e)}")
            if DEBUG and description:
                self.save_debug_screenshot(f"click_{description}_error")
                
        return False
        
    def wait_for_image(
        self,
        image_name: str,
        timeout: int = 30,
        confidence: float = 0.9,
        description: Optional[str] = None
    ) -> bool:
        """
        Ожидает появления изображения на экране
        
        Args:
            image_name: Имя файла изображения
            timeout: Таймаут в секундах
            confidence: Уровень уверенности при поиске
            description: Описание для логирования
            
        Returns:
            True если изображение найдено, False если таймаут
        """
        start_time = time.time()
        image_path = os.path.join(IMG_PATH, image_name)
        
        while time.time() - start_time < timeout:
            try:
                if pyautogui.locateOnScreen(image_path, confidence=confidence):
                    if description:
                        logging.info(f"Found {description}")
                    return True
            except Exception:
                pass
            time.sleep(1)
            
        if description:
            logging.error(f"Timeout waiting for {description}")
        return False
        
    def type_text(self, text: str, interval: float = 0.1) -> None:
        """
        Печатает текст с заданным интервалом
        
        Args:
            text: Текст для ввода
            interval: Интервал между нажатиями клавиш
        """
        pyautogui.write(text, interval=interval)
        
    def press_keys(self, *keys: str) -> None:
        """
        Нажимает комбинацию клавиш
        
        Args:
            keys: Клавиши для нажатия
        """
        pyautogui.hotkey(*keys)
        
    def move_to_corner(self) -> None:
        """Перемещает курсор в угол экрана"""
        pyautogui.moveTo(0, 100)
        pyautogui.click(0, 100)
        
    def show_toolbars(self) -> None:
        """Показывает тулбары, двигая мышь по экрану"""
        width, height = pyautogui.size()
        y = (height / 2)
        pyautogui.moveTo(0, y, duration=0.5)
        pyautogui.moveTo(width - 1, y, duration=0.5)
        
    def save_debug_screenshot(self, name: str) -> None:
        """
        Сохраняет скриншот для отладки
        
        Args:
            name: Имя файла скриншота
        """
        if not DEBUG:
            return
            
        try:
            if not os.path.exists(DEBUG_PATH):
                os.makedirs(DEBUG_PATH)
                
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_{name}.png"
            filepath = os.path.join(DEBUG_PATH, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            logging.info(f"Saved debug screenshot: {filepath}")
            
        except Exception as e:
            logging.error(f"Failed to save debug screenshot: {str(e)}")
            
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Получает размеры экрана
        
        Returns:
            Кортеж (ширина, высота)
        """
        return pyautogui.size() 