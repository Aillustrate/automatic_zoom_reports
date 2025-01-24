import os
import logging
import subprocess
from typing import Dict
from pathlib import Path
from src.config import ENV_DEFAULTS

class EnvironmentManager:
    """Класс для управления окружением приложения"""
    
    @staticmethod
    def setup_environment() -> Dict[str, str]:
        """
        Настраивает окружение для работы приложения
        
        Returns:
            Словарь с настроенными переменными окружения
        """
        env = os.environ.copy()
        
        # Устанавливаем значения по умолчанию
        for key, value in ENV_DEFAULTS.items():
            if key not in env:
                env[key] = value
                
        # Настраиваем XDG_RUNTIME_DIR
        if 'XDG_RUNTIME_DIR' not in env:
            runtime_dir = f'/tmp/runtime-{os.getenv("USER", "zoomrec")}'
            os.makedirs(runtime_dir, exist_ok=True)
            os.chmod(runtime_dir, 0o700)
            env['XDG_RUNTIME_DIR'] = runtime_dir
            
        return env
        
    @staticmethod
    def ensure_pulseaudio(env: Dict[str, str]) -> bool:
        """
        Проверяет и запускает PulseAudio если необходимо
        
        Args:
            env: Словарь с переменными окружения
            
        Returns:
            True если PulseAudio запущен успешно, False в противном случае
        """
        try:
            # Проверяем статус PulseAudio
            result = subprocess.run(
                ['pulseaudio', '--check'],
                capture_output=True
            )
            
            if result.returncode == 0:
                logging.info("PulseAudio is already running")
                return True
                
            # Запускаем PulseAudio
            logging.info("Starting PulseAudio daemon...")
            subprocess.run(
                ['pulseaudio', '--start', '--exit-idle-time=-1'],
                env=env
            )
            
            # Даем время на запуск
            import time
            time.sleep(2)
            return True
            
        except FileNotFoundError:
            logging.error("PulseAudio not found! Please install pulseaudio package")
            return False
        except Exception as e:
            logging.error(f"Failed to start PulseAudio: {str(e)}")
            return False
            
    @staticmethod
    def setup_dbus(env: Dict[str, str]) -> Dict[str, str]:
        """
        Настраивает D-Bus сессию
        
        Args:
            env: Текущие переменные окружения
            
        Returns:
            Обновленный словарь с переменными окружения
        """
        if 'DBUS_SESSION_BUS_ADDRESS' not in env:
            try:
                dbus_output = subprocess.check_output(
                    ['dbus-launch', '--sh-syntax']
                ).decode()
                
                for line in dbus_output.split('\n'):
                    if '=' in line:
                        var, value = line.split('=', 1)
                        env[var] = value.strip('"')
                        
                logging.info("D-Bus session initialized")
                
            except Exception as e:
                logging.error(f"Failed to initialize D-Bus session: {str(e)}")
                
        return env
        
    @classmethod
    def prepare_environment(cls) -> Dict[str, str]:
        """
        Подготавливает все необходимое окружение для работы приложения
        
        Returns:
            Подготовленное окружение
        """
        env = cls.setup_environment()
        env = cls.setup_dbus(env)
        cls.ensure_pulseaudio(env)
        return env 