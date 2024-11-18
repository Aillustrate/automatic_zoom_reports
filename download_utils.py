import yt_dlp

def download_video_from_youtube(link, name='%(title)s'):
    ydl_opts = {
        'outtmpl': '{}.%(ext)s'.format(name),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        downloaded_file_path = ydl.prepare_filename(info_dict)
    print(f"Видео {downloaded_file_path} успешно загружено!")
    return downloaded_file_path