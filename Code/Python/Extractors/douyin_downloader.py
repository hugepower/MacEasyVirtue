import json
import os
import re
from datetime import datetime
from pathlib import Path

import httpx


class DouyinDownloader:
    def __init__(self, save_dir):
        """
        Initialize the downloader, set the save directory and create the directory if not exists.

        :param save_dir: The directory path where files will be saved.
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(
            parents=True, exist_ok=True
        )  # Create the folder if it doesn't exist
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/94.0.4606.76 Mobile/15E148 Safari/604.1",
            "Referer": "https://www.douyin.com",  # To simulate browser request
        }

    @staticmethod
    def timestamp_to_str(timestamp):
        """
        Convert timestamp to a string in the format YYYYMMDDHHMMSS.

        :param timestamp: The timestamp (could be in seconds or milliseconds)
        :return: The formatted timestamp as a string.
        """
        if timestamp > 1e10:  # Handle millisecond timestamps
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp).strftime("%Y%m%d%H%M%S")

    @staticmethod
    def is_valid_video_id(value):
        """
        Check if the video ID is valid (contains only letters and numbers).

        :param value: The video ID to validate.
        :return: True if valid, otherwise False.
        """
        return isinstance(value, str) and bool(re.fullmatch(r"[a-zA-Z0-9]+", value))

    def download(self, url, save_path, created_time):
        """
        Download the file from the URL, handle download progress and errors.

        :param url: The URL to download the file from.
        :param save_path: The path where the file will be saved.
        :param created_time: The creation time to set the file's timestamp.
        """
        if save_path.exists():  # Skip if the file already exists
            print(f"⚡ File already exists: {save_path.name}")
            return

        temp_path = save_path.with_suffix(".part")  # Temporary file during download
        try:
            # Start streaming the file download
            with httpx.stream("GET", url, headers=self.headers) as response:
                if response.status_code != 200:  # Check for successful status code
                    print(
                        f"❌ Download failed: {save_path.name}, Status Code: {response.status_code}"
                    )
                    return
                self._download_file_with_progress(
                    response, temp_path, save_path, created_time
                )

        except httpx.RequestError as e:
            # Handle request-specific errors (e.g., network issues)
            print(f"❌ Request failed for {url}: {e}")
            if temp_path.exists():
                temp_path.unlink()  # Remove partial file if download failed
        except Exception as e:
            # Handle any other exceptions
            print(f"❌ Download error: {e}")
            if temp_path.exists():
                temp_path.unlink()  # Remove partial file if an error occurred

    def _download_file_with_progress(
        self, response, temp_path, save_path, created_time
    ):
        """
        Helper method to download a file with progress indication.

        :param response: The response object from the HTTP request.
        :param temp_path: The temporary path where the file will be saved during download.
        :param save_path: The final path where the file will be saved after download.
        :param created_time: The creation time to set the file's timestamp.
        """
        chunk_size = 10240  # Size of each chunk to download (10 KB)
        total_size = int(response.headers.get("content-length", 0))  # Total file size
        downloaded_size = 0  # Size of the downloaded content so far

        # Write the downloaded content to a temporary file
        with open(temp_path, "wb") as file:
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                file.write(chunk)
                downloaded_size += len(chunk)
                percent = (downloaded_size / total_size) * 100 if total_size else 0
                print(
                    f"\r📥 Download progress: {save_path.name} - {percent:.2f}%", end=""
                )

        # Rename the temporary file to the final file name
        os.rename(temp_path, save_path)
        os.utime(save_path, (created_time, created_time))  # Set file's timestamp
        print("\n✅ Download completed:", save_path.name)

    def download_image(self, image_url, user_id, created_time, filename_suffix):
        """
        Download an image with a unique filename.

        :param image_url: The URL of the image to download.
        :param user_id: The user ID associated with the image.
        :param created_time: The creation time to set the file's timestamp.
        :param filename_suffix: Suffix to append to the image filename.
        """
        image_name = f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{filename_suffix}.jpeg"
        image_path = self.save_dir / image_name
        self._download_if_not_exists(image_url, image_path, created_time)

    def download_video(self, video_url, user_id, created_time, video_id):
        """
        Download a video with a unique filename.

        :param video_url: The URL of the video to download.
        :param user_id: The user ID associated with the video.
        :param created_time: The creation time to set the file's timestamp.
        :param video_id: The video ID to generate the filename.
        """
        video_name = (
            f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{video_id}.mp4"
        )
        video_path = self.save_dir / video_name
        self._download_if_not_exists(video_url, video_path, created_time)

    def _download_if_not_exists(self, url, save_path, created_time):
        """
        Download a file if it does not already exist at the specified path.

        :param url: The URL of the file to download.
        :param save_path: The path where the file will be saved.
        :param created_time: The creation time to set the file's timestamp.
        """
        if not save_path.exists():  # Only download if the file doesn't exist
            self.download(url, save_path, created_time)

    def process_data(self, merged_data_path):
        """
        Process the data file, download videos and images, and handle missing data.

        :param merged_data_path: The path to the data file containing video and image information.
        """
        # Read and parse the JSON data from the file
        aweme_list_data = json.loads(merged_data_path.read_text())

        for aweme_item in aweme_list_data:
            aweme_list = aweme_item.get("aweme_list", [])
            if not aweme_list:  # Skip if no aweme list found
                continue

            for aweme in aweme_list:
                user_id = aweme.get("author", {}).get("uid", "unknown")
                created_time = aweme.get("create_time", 0)
                video_id = aweme.get("video", {}).get("play_addr", {}).get("uri", "")
                video_url = (
                    aweme.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
                )

                if self.is_valid_video_id(
                    video_id
                ):  # If valid video ID, download video
                    self.download_video(video_url, user_id, created_time, video_id)
                else:  # If video ID is not valid, process images
                    self._process_images(aweme, user_id, created_time)

        print("\n✅ Operation completed!")

    def _process_images(self, aweme, user_id, created_time):
        """
        Process images (including live photos) and download them.

        :param aweme: The aweme data containing the images to process.
        :param user_id: The user ID associated with the images.
        :param created_time: The creation time to set the file's timestamp.
        """
        for image_item in aweme.get("images", []):
            if not image_item.get("url_list"):  # Skip if no URL list available
                print(f"⚠️ Skipping image with missing URL list for user {user_id}")
                continue

            live_photo_uri = (
                image_item.get("video", {}).get("play_addr", {}).get("uri", "")
            )
            img_url = image_item.get("url_list", [])[-1]  # Get the last URL in the list

            if live_photo_uri and self.is_valid_video_id(live_photo_uri):
                # If it's a live photo, download the associated video and image
                self._download_live_photo(
                    image_item, user_id, created_time, live_photo_uri, img_url
                )
            else:
                # Otherwise, just download the image
                img_basename = image_item.get("uri", "").split("/")[-1]
                self.download_image(img_url, user_id, created_time, img_basename)

    def _download_live_photo(
        self, image_item, user_id, created_time, live_photo_uri, img_url
    ):
        """
        Download live photo (video file) and associated image.

        :param image_item: The image item containing live photo information.
        :param user_id: The user ID associated with the media.
        :param created_time: The creation time to set the file's timestamp.
        :param live_photo_uri: The URI of the live photo.
        :param img_url: The URL of the image.
        """
        live_photo_url = (
            image_item.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
        )
        live_photo_name = f"douyin_{user_id}_{self.timestamp_to_str(created_time)}_{live_photo_uri}.mov"
        live_photo_path = self.save_dir / live_photo_name
        self._download_if_not_exists(live_photo_url, live_photo_path, created_time)
        self.download_image(img_url, user_id, created_time, live_photo_uri)


# Example usage
save_directory = "/Users/AI/Downloads/www.douyin.com/"
downloader = DouyinDownloader(save_directory)

# Load data and start downloading
merged_data_file = Path(save_directory) / "user_all_aweme_data.json"
downloader.process_data(merged_data_file)
