from typing import Optional
import os
import logging
from pathlib import Path

# Logging configuration
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

# Debug mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Paths
BASE_PATH = Path(os.getenv('HOME', ''))
CSV_PATH = BASE_PATH / "meetings.csv"
IMG_PATH = BASE_PATH / "img"
REC_PATH = BASE_PATH / "recordings"
AUDIO_PATH = BASE_PATH / "audio"
DEBUG_PATH = REC_PATH / "screenshots" if DEBUG else None

# Telegram configuration
TELEGRAM_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID: Optional[str] = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_RETRIES: int = 5

# Display configuration
DISPLAY_NAME = os.getenv('DISPLAY_NAME', '')
if not DISPLAY_NAME or len(DISPLAY_NAME) < 3:
    DEFAULT_NAMES = [
        'iPhone', 'iPad', 'Macbook', 'Desktop', 'Huawei',
        'Mobile', 'PC', 'Windows', 'Home', 'MyPC',
        'Computer', 'Android'
    ]
    import random
    DISPLAY_NAME = random.choice(DEFAULT_NAMES)

# Time format
TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
CSV_DELIMITER = ';'

# FFmpeg configuration
FFMPEG_CMD_TEMPLATE = (
    "ffmpeg -nostats -loglevel {loglevel} -f pulse -ac 2 -i 1 "
    "-f x11grab -r 30 -s {resolution} -i {display} "
    "-acodec pcm_s16le -vcodec libx264rgb -preset ultrafast "
    "-crf 0 -threads 0 -async 1 -vsync 1 {output}"
)

# Environment configuration
ENV_DEFAULTS = {
    'DISPLAY': ':0',
    'QT_PLUGIN_PATH': '/opt/zoom/Qt/plugins',
    'LD_LIBRARY_PATH': '/opt/zoom/Qt/lib:/opt/zoom',
    'QT_QPA_PLATFORM_PLUGIN_PATH': '/opt/zoom/Qt/plugins/platforms',
    'XDG_SESSION_TYPE': 'x11',
    'XDG_CURRENT_DESKTOP': 'XFCE'
} 