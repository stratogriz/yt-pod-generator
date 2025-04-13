import os
import json
import yt_dlp
from pydub import AudioSegment
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone


# Constants
CHANNEL_URL = 'https://www.youtube.com/@DanMohlerSR/videos'
AUDIO_OUTPUT_DIR = 'audio'
PODCAST_OUTPUT_FILE = 'podcast.xml'

# Ensure directories exist
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio[abr<=128k]',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
    'playlistend': 10,
    'outtmpl': f'{AUDIO_OUTPUT_DIR}/%(title)s.%(ext)s',
    # Filter videos between 8 minutes and 1 hour 40 min
    'match_filter': yt_dlp.utils.match_filter_func('duration >= 480'),
}


def download_audio():
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #ydl.download([CHANNEL_URL])
        #ydl.download(['https://www.youtube.com/watch?v=VOTjzVZihfM'])
        #ydl.download(['https://www.youtube.com/@JOGS.STUDIO/videos'])
        ydl.download(['https://www.youtube.com/watch?v=pKBTU3EPViM'])


def generate_podcast():
    fg = FeedGenerator()
    fg.load_extension('podcast')

    fg.title('TR - Dan Mohler YT Archives')
    fg.link(href='http://example.com', rel='alternate')
    fg.description('A podcast of my favorite YouTube channel.')
    fg.language('en')

    for audio_file in os.listdir(AUDIO_OUTPUT_DIR):
        print(audio_file)
        if audio_file.endswith('.mp3'):
            fe = fg.add_entry()
            fe.title(audio_file)
            fe.enclosure(
                f'https://stratogriz.github.io/yt-pod-generator/audio/{audio_file}', 0,
                'audio/mpeg'
            )
            dt = datetime.now()
            dt = dt.replace(tzinfo=timezone.utc)
            fe.pubDate(dt)

    fg.rss_file(PODCAST_OUTPUT_FILE)


def main():
    download_audio()
    generate_podcast()


if __name__ == '__main__':
    main()
