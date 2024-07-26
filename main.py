import os
import json
import yt_dlp
from pydub import AudioSegment
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Constants
CHANNEL_URL = 'https://www.youtube.com/@DanMohlerSR/videos'
AUDIO_OUTPUT_DIR = '/tmp/audio_files'
AUDIO_OUTPUT_DIR = 'audio'
PODCAST_OUTPUT_FILE = 'podcast.xml'
GDRIVE_FOLDER_ID = os.environ['GDRIVE_FOLDER_ID']

# Ensure directories exist
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Save the Google credentials from the secret to a file
# with open('/tmp/credentials.json', 'w') as f:
#    f.write(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'playlistend': 1,
    'outtmpl': f'{AUDIO_OUTPUT_DIR}/%(title)s.%(ext)s',
}

# need to filter for downloaded already...
# query gdrive and make list and check for presence...
# or query the xml...


def download_audio():
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([CHANNEL_URL])


def upload_to_gdrive(file_path, mime_type):
    creds = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    credentials = Credentials.from_service_account_info(creds)
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [GDRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')


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
            audio_file_path = os.path.join(AUDIO_OUTPUT_DIR, audio_file)
            # file_id = upload_to_gdrive(audio_file_path, 'audio/mpeg')
            # file_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            fe = fg.add_entry()
            fe.title(audio_file)
            fe.enclosure(audio_file, 0, 'audio/mpeg')
            dt = datetime.now()
            dt = dt.replace(tzinfo=timezone.utc)

            fe.pubDate(dt)

    fg.rss_file(PODCAST_OUTPUT_FILE)
    # upload_to_gdrive(PODCAST_OUTPUT_FILE, 'application/rss+xml')


def main():
    download_audio()
    generate_podcast()


if __name__ == '__main__':
    main()
