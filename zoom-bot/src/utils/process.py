import os
import signal
import logging
import psutil
from typing import List, Dict, Optional

def find_process_by_name(process_name: str) -> List[Dict[str, any]]:
    """
    Находит все процессы по имени
    
    Args:
        process_name: Имя процесса для поиска
        
    Returns:
        Список словарей с информацией о найденных процессах
    """
    processes = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if process_name.lower() in pinfo['name'].lower():
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_process(pid: int) -> bool:
    """
    Завершает процесс по PID
    
    Args:
        pid: ID процесса
        
    Returns:
        True если процесс успешно завершен, False в противном случае
    """
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except Exception as ex:
        logging.error(f"Could not terminate process [{pid}]: {str(ex)}")
        return False

def exit_process_by_name(name: str) -> None:
    """
    Завершает все процессы с указанным именем
    
    Args:
        name: Имя процесса
    """
    processes = find_process_by_name(name)
    if processes:
        logging.info(f"{name} process exists | killing..")
        for proc in processes:
            kill_process(proc['pid'])

def run_process(
    command: str,
    shell: bool = True,
    preexec_fn: Optional[callable] = None
) -> Optional[psutil.Process]:
    """
    Запускает новый процесс
    
    Args:
        command: Команда для запуска
        shell: Использовать ли shell
        preexec_fn: Функция для выполнения в дочернем процессе
        
    Returns:
        Объект процесса или None в случае ошибки
    """
    try:
        import subprocess
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=preexec_fn
        )
        return process
    except Exception as e:
        logging.error(f"Failed to start process: {str(e)}")
        return None 