import os
import time
import random
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

LINKS_FILE = "links.txt"
COMPLETED_FILE = "completed.txt"
DOWNLOAD_FOLDER = "downloads"
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def read_file(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return [line.strip() for line in f if line.strip()]


def append_completed(link):
    with open(COMPLETED_FILE, "a") as f:
        f.write(link + "\n")


def download_video(link):
    print(f"Downloading: {link}")
    subprocess.run([
        "yt-dlp",
        "-o",
        f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        link
    ], check=True)


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

    print("Uploaded to Drive:", filepath)


def main():
    links = set(read_file(LINKS_FILE))
    completed = set(read_file(COMPLETED_FILE))

    new_links = links - completed

    if not new_links:
        print("No new links found.")
        return

    for link in new_links:
        try:
            download_video(link)

            latest_file = max(
                [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)],
                key=os.path.getctime
            )

            upload_to_drive(latest_file)
            append_completed(link)

            delay = random.randint(5, 15)
            print(f"Sleeping {delay} sec...")
            time.sleep(delay)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
