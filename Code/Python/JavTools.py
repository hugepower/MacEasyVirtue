"""
Author: hugepower
Date: 2023-05-03 16:34:27
LastEditors: hugepower
LastEditTime: 2023-05-04 10:03:41
Description: This is a tool that can match local and web movies with Tampermonkey scripts
"""
import argparse
import logging
import os
import re
import subprocess
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="Logs/javbus-logs.log",
    filemode="a",
)


class MovieFinder:
    """
    A class that finds movies from a source (file or directory) and returns a dictionary of movie ids and paths
    """

    def __init__(self, source: Path):
        self.source = source
        self.movie_dict = {}
        self.rattern = re.compile(r"[A-Za-z]+(-)(\d+)", re.IGNORECASE)
        self.extensions = (".mkv", ".avi", ".mp4", ".iso")

    def is_movie_file(self, file):
        """
        Check if a file is a movie file based on its extension

        Args:
            file (Path): A Path object that represents a file.

        Returns:
            bool: True if the file is a movie file, False otherwise.
        """
        return file.is_file() and file.suffix in self.extensions

    def get_movie_id(self, file):
        """
        Extract the movie id from a file name using a regex pattern

        Args:
            file (Path or str): A Path object or a string that represents a file name.

        Returns:
            str or None: The movie id if found, None otherwise.
        """
        ids = self.rattern.search(file.stem if isinstance(file, Path) else file)
        if ids is not None:
            return ids.group(0).upper()
        return None

    def find_movies(self):
        """
        Find movies from the source and populate the movie dictionary
        """
        if self.source.is_dir():
            files = filter(self.is_movie_file, self.source.rglob("*.*"))
        elif self.source.is_file():
            with open(self.source, mode="r", encoding="UTF-8") as f:
                files = f.readlines()
        else:
            logging.warning("No movie information was found: %s", self.source)
            return
        for file in files:
            movie_id = self.get_movie_id(file)
            if movie_id is not None:
                self.movie_dict.setdefault(movie_id, file)

    def get_movie_dict(self):
        """
        Return the movie dictionary
        """
        return self.movie_dict


class MovieHandler(FileSystemEventHandler):
    """
    A class that handles file system events and updates the movie finder accordingly
    """

    def __init__(self, finder):
        self.finder = finder

    def on_created(self, event):
        """
        Handle the creation of a new file or directory
        """
        logging.info("Created %s", event.src_path)
        self.finder.find_movies()

    def on_deleted(self, event):
        """
        Handle the deletion of a file or directory
        """
        logging.info("Deleted %s", event.src_path)
        self.finder.find_movies()

    def on_modified(self, event):
        """
        Handle the modification of a file or directory
        """
        if self.finder.source.is_file():
            logging.info("Modified %s", event.src_path)
            self.finder.find_movies()

    def on_moved(self, event):
        """
        Handle the moving or renaming of a file or directory
        """
        logging.info("Moved %s to %s", event.src_path, event.dest_path)
        self.finder.find_movies()


class SearchData(BaseModel):
    movie_id: str


class MovieAPI(FastAPI):
    def __init__(self, source: Path):
        super().__init__()
        self.source = source
        self.finder = MovieFinder(self.source)
        self.finder.find_movies()
        self.add_api_route("/javbus/", self.get_movie_info, methods=["GET"])
        self.add_api_route("/javbus/post/", self.post_movie_info, methods=["POST"])

    def log_and_return(self, status: str, message: str) -> dict:
        if status == "success":
            logging.info(message)
        else:
            logging.error(message)
        return {
            "status": status,
            "message": message,
        }

    def get_movie_info(self) -> dict:
        return self.finder.get_movie_dict()

    def post_movie_info(self, data: SearchData) -> dict:
        """
          Post movie information to Telegram.

        Args:
            data: A SearchData object containing the movie ID and other information.

        Returns:
            A dictionary containing the status and message of the posting.

        Raises:
            KeyError: If the movie ID is not found in the movie dictionary.
            OSError: If the movie file is not a valid video file or IINA is not installed.
        """
        movie_dict = self.finder.get_movie_dict()
        movie_id = data.movie_id
        movie_path = movie_dict.get(movie_id)
        self.open_with_iina(movie_path)

    def open_with_iina(self, path):
        """
        Open a video file with IINA player.

        Args:
            path: A string representing the path of the video file.

        Returns:
            A dictionary containing the status and message of the operation.

        Examples:
            >>> open_with_iina("/Users/xxx/Movies/test.mp4")
            {"status": "success", "message": "Opened /Users/xxx/Movies/test.mp4 with IINA"}
            >>> open_with_iina("/Users/xxx/Movies/nonexistent.mp4")
            {"status": "error", "message": "File /Users/xxx/Movies/nonexistent.mp4 does not exist."}
        """
        if not os.path.isfile(path):
            error_message = f"File {path} does not exist."
            return self.log_and_return("error", error_message)
        with subprocess.Popen(
            ["open", "-a", "IINA", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            _, error = process.communicate()
            if process.returncode == 0:
                error_message = f"Opened {path} with IINA"
                return self.log_and_return("success", error_message)
            error_message = f"Failed to open movie with IINA: {error.decode()}"
            return self.log_and_return("error", error_message)


def run_app_and_observer(source: Path):
    """
    Run the observer and the app with a given source.
    """
    app = MovieAPI(source)
    handler = MovieHandler(app.finder)
    observer = Observer()
    is_recursive = source.is_dir()
    observer.schedule(handler, source.as_posix(), recursive=is_recursive)
    observer.start()
    uvicorn.run(app=app, host="127.0.0.1", port=8082)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the movie API and observer.")
    parser.add_argument(
        "input_path", type=Path, help="The path to the movie data folder or list file."
    )
    args = parser.parse_args()
    input_path = Path(args.input_path)
    if input_path.exists():
        run_app_and_observer(input_path)
    else:
        logging.warning("The path is invalid: %s", input_path)
