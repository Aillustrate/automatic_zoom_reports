import csv
import logging
import schedule
import time
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.config import CSV_PATH, CSV_DELIMITER
from src.meeting import MeetingInfo, MeetingManager

@dataclass
class ScheduledMeeting:
    """Запланированная встреча"""
    weekday: str
    time: str
    id: str
    password: str
    duration: int  # в минутах
    description: str
    record: bool

class MeetingScheduler:
    """Класс для планирования встреч"""
    
    def __init__(self):
        self.meeting_manager = MeetingManager()
        
    def load_meetings(self) -> List[ScheduledMeeting]:
        """
        Загружает встречи из CSV файла
        
        Returns:
            Список запланированных встреч
        """
        meetings = []
        try:
            with open(CSV_PATH, mode='r') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=CSV_DELIMITER)
                for row in reader:
                    meeting = ScheduledMeeting(
                        weekday=row['weekday'],
                        time=row['time'],
                        id=row['id'],
                        password=row['password'],
                        duration=int(row['duration']),
                        description=row['description'],
                        record=row['record'].lower() == 'true'
                    )
                    meetings.append(meeting)
        except Exception as e:
            logging.error(f"Failed to load meetings: {str(e)}")
            
        return meetings
        
    def setup_schedule(self) -> None:
        """Настраивает расписание встреч"""
        meetings = self.load_meetings()
        count = 0
        
        for meeting in meetings:
            if meeting.record:
                # Планируем на минуту раньше для подготовки
                schedule_time = (
                    datetime.strptime(meeting.time, '%H:%M') -
                    timedelta(minutes=1)
                ).strftime('%H:%M')
                
                # Создаем задачу для планировщика
                getattr(schedule.every(), meeting.weekday.lower()).at(
                    schedule_time
                ).do(
                    self.join_scheduled_meeting,
                    meeting=meeting
                )
                count += 1
                
        logging.info(f"Added {count} meetings to schedule")
        
    def join_scheduled_meeting(self, meeting: ScheduledMeeting) -> None:
        """
        Присоединяется к запланированной встрече
        
        Args:
            meeting: Запланированная встреча
        """
        meeting_info = MeetingInfo(
            id=meeting.id,
            password=meeting.password,
            duration=meeting.duration * 60,  # конвертируем в секунды
            description=meeting.description
        )
        self.meeting_manager.join_meeting(meeting_info)
        
    def join_ongoing_meeting(self) -> None:
        """Присоединяется к текущей встрече если она есть"""
        meetings = self.load_meetings()
        curr_date = datetime.now()
        
        for meeting in meetings:
            if not meeting.record:
                continue
                
            # Проверяем день недели
            if meeting.weekday.lower() != curr_date.strftime('%A').lower():
                continue
                
            # Парсим время начала
            start_time = datetime.strptime(meeting.time, '%H:%M').time()
            start_date = curr_date.replace(
                hour=start_time.hour,
                minute=start_time.minute,
                second=0,
                microsecond=0
            )
            
            # Вычисляем время окончания
            end_date = start_date + timedelta(minutes=meeting.duration)
            
            # Проверяем идет ли встреча сейчас
            if start_date <= curr_date <= end_date:
                # Вычисляем оставшуюся длительность
                remaining_duration = (end_date - curr_date).total_seconds()
                
                meeting_info = MeetingInfo(
                    id=meeting.id,
                    password=meeting.password,
                    duration=int(remaining_duration),
                    description=meeting.description
                )
                self.meeting_manager.join_meeting(meeting_info)
                break
                
    def run(self) -> None:
        """Запускает планировщик"""
        self.setup_schedule()
        self.join_ongoing_meeting()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
            # Показываем время до следующей встречи
            next_run = schedule.next_run()
            if next_run:
                remaining = next_run - datetime.now()
                print(f"Next meeting in {remaining}", end="\r", flush=True) 