import os
import signal
import logging
import subprocess
import atexit
from typing import Optional
from datetime import datetime
from pathlib import Path

from src.config import (
    REC_PATH,
    TIME_FORMAT,
    FFMPEG_CMD_TEMPLATE
)

class Recorder:
    """Класс для записи экрана и звука"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_path: Optional[Path] = None
        
    def start_recording(
        self,
        description: str,
        resolution: str,
        display: str,
        loglevel: str = "error"
    ) -> bool:
        """
        Начинает запись экрана и звука
        
        Args:
            description: Описание записи
            resolution: Разрешение экрана
            display: Идентификатор дисплея
            loglevel: Уровень логирования ffmpeg
            
        Returns:
            True если запись начата успешно, False в противном случае
        """
        try:
            # Создаем директорию для записей если не существует
            os.makedirs(REC_PATH, exist_ok=True)
            
            # Формируем имя файла
            timestamp = datetime.now().strftime(TIME_FORMAT)
            filename = f"{timestamp}-{description}.mkv"
            self.output_path = Path(REC_PATH) / filename
            
            # Формируем команду
            command = FFMPEG_CMD_TEMPLATE.format(
                loglevel=loglevel,
                resolution=resolution,
                display=display,
                output=str(self.output_path)
            )
            
            # Запускаем процесс записи
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Регистрируем обработчик для корректного завершения
            atexit.register(self.stop_recording)
            
            logging.info(f"Started recording to {self.output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start recording: {str(e)}")
            return False
            
    def stop_recording(self) -> None:
        """Останавливает запись"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGQUIT)
                atexit.unregister(self.stop_recording)
                self.process = None
                logging.info("Recording stopped")
            except Exception as e:
                logging.error(f"Failed to stop recording: {str(e)}")
                
    def is_recording(self) -> bool:
        """
        Проверяет, идет ли запись
        
        Returns:
            True если запись идет, False в противном случае
        """
        return self.process is not None and self.process.poll() is None
        
    def get_output_path(self) -> Optional[Path]:
        """
        Возвращает путь к файлу записи
        
        Returns:
            Path к файлу записи или None если запись не начата
        """
        return self.output_path 