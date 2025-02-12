import json
import os
import re
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
        """Convert timestamp to string format YYYYMMDDHHMMSS"""
        if timestamp > 1e10:  # Handle milliseconds timestamp
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp).strftime("%Y%m%d%H%M%S")

    @staticmethod
    def is_valid_video_id(value):
        """Check if video_id is valid (only contains letters and numbers)"""
        return isinstance(value, str) and bool(re.fullmatch(r"[a-zA-Z0-9]+", value))

    def download(self, url, save_path, created_time):
        """Download video or image"""
        if save_path.exists():
            print(f"⚡ File already exists: {save_path.name}")
            return

        temp_path = save_path.with_suffix(".part")  # Temporary file for download
        try:
            with httpx.stream("GET", url, headers=self.headers) as response:
                if response.status_code != 200:
                    print(
                        f"❌ Download failed: {save_path.name}, Status Code: {response.status_code}"
                    )
                    return

                chunk_size = 10240
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0

                with open(temp_path, "wb") as file:
                    for chunk in response.iter_bytes(chunk_size=chunk_size):
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        percent = (
                            (downloaded_size / total_size) * 100 if total_size else 0
                        )
                        print(
                            f"\r📥 Download progress: {save_path.name} - {percent:.2f}%",
                            end="",
                        )

                os.rename(temp_path, save_path)
                os.utime(save_path, (created_time, created_time))
                print("\n✅ Download completed:", save_path.name)

        except Exception as e:
            print(f"❌ Download error: {e}")
            if temp_path.exists():
                temp_path.unlink()

    def download_image(self, image_url, user_id, created_time, filename_suffix):
        """Download image (avoiding duplicate code)"""
        image_name = f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{filename_suffix}.jpeg"
        image_path = self.save_dir / image_name
        if not image_path.exists():
            self.download(image_url, image_path, created_time)

    def process_data(self, merged_data_path):
        """Process and download videos and images from the data file"""
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

                if not self.is_valid_video_id(video_id):
                    try:
                        for image_item in aweme.get("images", []):
                            live_photo_uri = (
                                image_item.get("video", {})
                                .get("play_addr", {})
                                .get("uri", "")
                            )
                            img_url = image_item.get("url_list", [])[
                                -1
                            ]  # Get the last URL

                            if live_photo_uri and self.is_valid_video_id(
                                live_photo_uri
                            ):
                                # Download live photo (mov)
                                live_photo_url = (
                                    image_item.get("video", {})
                                    .get("play_addr", {})
                                    .get("url_list", [""])[0]
                                )
                                live_photo_name = f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{live_photo_uri}.mov"
                                live_photo_path = self.save_dir / live_photo_name
                                if not live_photo_path.exists():
                                    self.download(
                                        live_photo_url, live_photo_path, created_time
                                    )

                                # Download corresponding jpeg image
                                self.download_image(
                                    img_url, user_id, created_time, live_photo_uri
                                )

                            else:
                                # Only download image
                                img_basename = image_item.get("uri", "").split("/")[-1]
                                self.download_image(
                                    img_url, user_id, created_time, img_basename
                                )

                    except Exception as e:
                        print(f"⚠️ Error processing images: {e}")
                    continue

                # Only video
                video_name = f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{video_id}.mp4"
                video_path = self.save_dir / video_name
                if not video_path.exists():
                    self.download(video_url, video_path, created_time)

        print("\n✅ Operation completed!")


# Example usage
save_directory = "/Users/AI/Downloads/www.douyin.com/"
downloader = DouyinDownloader(save_directory)

# Load data and start downloading
merged_data_file = Path(save_directory) / "user_all_aweme_data.json"
downloader.process_data(merged_data_file)
