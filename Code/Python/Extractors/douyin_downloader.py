import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import httpx


class DouyinDownloader:
    def __init__(self, save_dir):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/94.0.4606.76 Mobile/15E148 Safari/604.1",
            "Referer": "https://www.douyin.com",
        }

    @staticmethod
    def timestamp_to_str(timestamp):
        if timestamp > 1e10:
            timestamp /= 1000
        return datetime.fromtimestamp(timestamp).strftime("%Y%m%d%H%M%S")

    @staticmethod
    def is_valid_video_id(value):
        return isinstance(value, str) and bool(re.fullmatch(r"[a-zA-Z0-9]+", value))

    def download(self, url, save_path, created_time):
        if save_path.exists():
            print(f"⚡ File already exists: {save_path.name}")
            return
        temp_path = save_path.with_suffix(".part")
        try:
            with httpx.stream("GET", url, headers=self.headers) as response:
                if response.status_code != 200:
                    print(
                        f"❌ Download failed: {save_path.name}, Status Code: {response.status_code}"
                    )
                    return
                self._download_file_with_progress(
                    response, temp_path, save_path, created_time
                )
        except httpx.RequestError as e:
            print(f"❌ Request failed for {url}: {e}")
            if temp_path.exists():
                temp_path.unlink()
        except Exception as e:
            print(f"❌ Download error: {e}")
            if temp_path.exists():
                temp_path.unlink()

    def _download_file_with_progress(
        self, response, temp_path, save_path, created_time
    ):
        chunk_size = 10240
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        with open(temp_path, "wb") as file:
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                file.write(chunk)
                downloaded_size += len(chunk)
                percent = (downloaded_size / total_size) * 100 if total_size else 0
                print(
                    f"\r📥 Download progress: {save_path.name} - {percent:.2f}%", end=""
                )
        os.rename(temp_path, save_path)
        os.utime(save_path, (created_time, created_time))
        print("\n✅ Download completed:", save_path.name)

    def process_data(self, merged_data_path):
        aweme_list_data = json.loads(merged_data_path.read_text())
        for aweme_item in aweme_list_data:
            aweme_list = aweme_item.get("aweme_list", [])
            if not aweme_list:
                continue
            for aweme in aweme_list:
                user_id = aweme.get("author", {}).get("uid", "unknown")
                created_time = aweme.get("create_time", 0)
                video_id = aweme.get("video", {}).get("play_addr", {}).get("uri", "")
                video_url = (
                    aweme.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
                )
                if self.is_valid_video_id(video_id):
                    self.download_video(video_url, user_id, created_time, video_id)
                else:
                    self._process_images(aweme, user_id, created_time)
        print("\n✅ Operation completed!")

    def download_video(self, video_url, user_id, created_time, video_id):
        video_name = (
            f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{video_id}.mp4"
        )
        video_path = self.save_dir / video_name
        self._download_if_not_exists(video_url, video_path, created_time)

    def _process_images(self, aweme, user_id, created_time):
        for image_item in aweme.get("images", []):
            if not image_item.get("url_list"):
                print(f"⚠️ Skipping image with missing URL list for user {user_id}")
                continue
            img_url = image_item.get("url_list", [])[-1]
            img_basename = image_item.get("uri", "").split("/")[-1]
            self.download_image(img_url, user_id, created_time, img_basename)

    def download_image(self, image_url, user_id, created_time, filename_suffix):
        image_name = f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{filename_suffix}.jpeg"
        image_path = self.save_dir / image_name
        self._download_if_not_exists(image_url, image_path, created_time)

    def _download_if_not_exists(self, url, save_path, created_time):
        if not save_path.exists():
            self.download(url, save_path, created_time)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <save_directory>")
        sys.exit(1)
    save_directory = sys.argv[1]
    downloader = DouyinDownloader(save_directory)
    merged_data_file = Path(save_directory) / "user_all_aweme_data.json"
    if not merged_data_file.exists():
        print(f"❌ Data file not found: {merged_data_file}")
        sys.exit(1)
    downloader.process_data(merged_data_file)
