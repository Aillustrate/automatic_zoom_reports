import os
import time
import logging
import threading
from typing import Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.config import DISPLAY_NAME
from src.utils.process import exit_process_by_name, run_process
from src.utils.environment import EnvironmentManager
from src.ui.automation import UIAutomation
from src.recorder import Recorder
from src.utils.telegram import notifier

@dataclass
class MeetingInfo:
    """Информация о встрече"""
    id: str
    password: str
    duration: int  # в секундах
    description: str
    
class MeetingManager:
    """Класс для управления встречами Zoom"""
    
    def __init__(self):
        self.ui = UIAutomation()
        self.recorder = Recorder()
        self.ongoing_meeting = False
        self.video_panel_hidden = False
        
    def join_meeting(self, meeting: MeetingInfo) -> bool:
        """
        Присоединяется к встрече Zoom
        
        Args:
            meeting: Информация о встрече
            
        Returns:
            True если успешно присоединились, False в противном случае
        """
        logging.info(f"Joining meeting: {meeting.description}")
        
        # Подготавливаем окружение
        env = EnvironmentManager.prepare_environment()
        
        # Закрываем Zoom если запущен
        exit_process_by_name("zoom")
        
        # Определяем тип подключения
        is_url = meeting.id.startswith(('https://', 'http://'))
        
        # Запускаем Zoom
        if not self._start_zoom(meeting.id, is_url, env):
            return False
            
        # Ждем загрузки Zoom
        time.sleep(5)
        
        # Присоединяемся к встрече
        if is_url:
            joined = self._join_by_url()
        else:
            joined = self._join_by_id(meeting.id, meeting.password)
            
        if not joined:
            notifier.send_message(f"Failed to join meeting {meeting.description}!")
            return False
            
        # Настраиваем аудио
        if not self._setup_audio():
            return False
            
        # Настраиваем отображение
        self._setup_display()
        
        # Запускаем запись
        self._start_recording(meeting)
        
        # Запускаем мониторинг встречи
        self._start_monitoring()
        
        notifier.send_message(
            f"Joined Meeting '{meeting.description}' and started recording."
        )
        
        return True
        
    def _start_zoom(self, meeting_id: str, is_url: bool, env: Dict[str, str]) -> bool:
        """Запускает клиент Zoom"""
        command = f'zoom --url="{meeting_id}"' if is_url else "zoom"
        process = run_process(command, env=env)
        return process is not None
        
    def _join_by_url(self) -> bool:
        """Присоединяется к встрече по URL"""
        time.sleep(10)  # Ждем загрузки страницы
        
        # Вводим имя
        self.ui.press_keys('ctrl', 'a')
        self.ui.type_text(DISPLAY_NAME)
        
        # Настраиваем опции
        for _ in range(3):
            self.ui.press_keys('tab')
            self.ui.press_keys('space')
            
        return self._check_join_status()
        
    def _join_by_id(self, meeting_id: str, password: str) -> bool:
        """Присоединяется к встрече по ID"""
        if not self.ui.find_and_click('join_meeting.png', description="Join Meeting button"):
            return False
            
        time.sleep(2)
        
        # Вводим ID встречи
        self.ui.press_keys('tab', 'tab')
        self.ui.type_text(meeting_id)
        
        # Вводим имя
        self.ui.press_keys('tab', 'tab')
        self.ui.press_keys('ctrl', 'a')
        self.ui.type_text(DISPLAY_NAME)
        
        # Настраиваем опции
        for _ in range(3):
            self.ui.press_keys('tab')
            self.ui.press_keys('space')
            
        time.sleep(2)
        
        if not self._check_join_status():
            return False
            
        # Вводим пароль
        self.ui.type_text(password)
        self.ui.press_keys('tab')
        self.ui.press_keys('space')
        
        return True
        
    def _check_join_status(self) -> bool:
        """Проверяет статус присоединения"""
        # TODO: Добавить проверки на различные ошибки
        return True
        
    def _setup_audio(self) -> bool:
        """Настраивает аудио"""
        time.sleep(2)
        return self.ui.find_and_click(
            'join_with_computer_audio.png',
            description="Join Audio button"
        )
        
    def _setup_display(self) -> None:
        """Настраивает отображение"""
        self.ui.show_toolbars()
        
        # Входим в полноэкранный режим
        self.ui.find_and_click('view.png', description="View button")
        time.sleep(2)
        self.ui.find_and_click('fullscreen.png', description="Fullscreen button")
        
        # Скрываем панель видео
        if self.ui.find_and_click('view_options.png', description="View Options"):
            self.ui.find_and_click(
                'hide_video_panel.png',
                description="Hide Video Panel"
            )
            self.video_panel_hidden = True
            
        # Перемещаем мышь в угол
        self.ui.move_to_corner()
        
    def _start_recording(self, meeting: MeetingInfo) -> None:
        """Начинает запись встречи"""
        width, height = self.ui.get_screen_size()
        resolution = f"{width}x{height}"
        display = os.getenv('DISPLAY', ':0')
        
        self.recorder.start_recording(
            description=meeting.description,
            resolution=resolution,
            display=display
        )
        
    def _start_monitoring(self) -> None:
        """Запускает мониторинг встречи"""
        self.ongoing_meeting = True
        
        def monitor():
            while self.ongoing_meeting:
                # Проверяем статус записи
                if self.ui.find_and_click(
                    'meeting_is_being_recorded.png',
                    description="Recording notification",
                    confidence=0.9
                ):
                    self.ui.find_and_click(
                        'got_it.png',
                        description="Got it button"
                    )
                    
                # Проверяем завершение встречи
                if self.ui.wait_for_image(
                    'meeting_ended_by_host_1.png',
                    timeout=5,
                    description="Meeting ended notification"
                ):
                    self.ongoing_meeting = False
                    logging.info("Meeting ended by host")
                    
                time.sleep(10)
                
        # Запускаем мониторинг в отдельном потоке
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()
        
    def end_meeting(self) -> None:
        """Завершает встречу"""
        self.ongoing_meeting = False
        self.recorder.stop_recording()
        exit_process_by_name("zoom") 