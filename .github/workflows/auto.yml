import os
import time
import random
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

LINKS_FILE = "links.txt"
COMPLETED_FILE = "completed.txt"
DOWNLOAD_DIR = "downloads"

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def read_lines(file):
    if not os.path.exists(file):
        return set()
    with open(file, "r") as f:
        return set(line.strip() for line in f if line.strip())


def append_completed(link):
    with open(COMPLETED_FILE, "a") as f:
        f.write(link + "\n")


def download_video(link):
    print(f"Downloading: {link}")
    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        link
    ], check=True)


def get_latest_file():
    files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)]
    if not files:
        return None
    return max(files, key=os.path.getctime)


def upload_to_drive(filepath):
    creds = Credentials.from_authorized_user_file("token.json")
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": os.path.basename(filepath),
        "parents": [DRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(filepath, resumable=True)

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print("Uploaded:", filepath)


def main():
    links = read_lines(LINKS_FILE)
    completed = read_lines(COMPLETED_FILE)

    new_links = links - completed

    if not new_links:
        print("No new links found.")
        return

    for link in new_links:
        try:
            download_video(link)

            file_path = get_latest_file()
            if file_path:
                upload_to_drive(file_path)
                append_completed(link)

                delay = random.randint(6, 18)
                print(f"Sleeping {delay} seconds...")
                time.sleep(delay)

        except Exception as e:
            print("Error processing:", link)
            print(e)


if __name__ == "__main__":
    main()
