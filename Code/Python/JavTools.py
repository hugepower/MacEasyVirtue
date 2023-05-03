'''
Author: hugepower
Date: 2023-05-03 16:34:27
LastEditors: hugepower
LastEditTime: 2023-05-03 17:17:58
Description: This is a tool that can match local and web movies with Tampermonkey scripts
'''
import logging
import re
import subprocess
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

app = FastAPI()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    filename="Logs/javbus-logs.log",
    filemode="a",
)

logger = logging.getLogger('Javbus_logger')
logger.propagate = False



MOVIE_DIR = "/Volumes/Movies/Javbus"
MOVIE_FILES_TXT = "/Volumes/Movies/movie_files.txt"
EXTENSIONS = (".mkv", ".avi", ".mp4", ".iso")
PATTERN = re.compile(r"[A-Za-z]+(-)(\d+)", re.IGNORECASE)


class MovieFinder:
    """
    A class that finds movies from a source (file or directory) and returns a dictionary of movie ids and paths
    """

    def __init__(self, source):
        self.source = source
        self.movie_dict = {}

    def is_movie_file(self, file):
        """
        Check if a file is a movie file based on its extension
        """
        return file.is_file() and file.suffix in EXTENSIONS

    def get_movie_id(self, file):
        """
        Extract the movie id from a file name using a regex pattern
        """
        ids = PATTERN.search(file.stem if isinstance(file, Path) else file)
        if ids is not None:
            return ids.group(0).upper()
        return None

    def find_movies(self):
        """
        Find movies from the source and populate the movie dictionary
        """
        if Path(self.source).is_dir():
            files = filter(self.is_movie_file, Path(self.source).rglob("*.*"))
        elif Path(self.source).is_file():
            with open(self.source, mode="r", encoding="UTF-8") as f:
                files = f.readlines()
        else:
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
        logging.info("Modified %s", event.src_path)
        self.finder.find_movies()

    def on_moved(self, event):
        """
        Handle the moving or renaming of a file or directory
        """
        logging.info("Moved %s to %s", event.src_path, event.dest_path)
        self.finder.find_movies()


@app.get("/javbus/")
def get_movie_info():
    """
    Return the movie information as a dictionary from a given source.

    Args:
        source (str): The path to the file or directory that contains the movie files.

    Returns:
        dict: A dictionary that maps the movie titles to their metadata.
    """
    finder = MovieFinder(MOVIE_DIR)
    finder.find_movies()
    return finder.get_movie_dict()


def log_and_return(status: str, message: str) -> dict:
    """Log and return the status and message of a post request.

    Args:
        status (str): The status of the post request, either "success" or "error".
        message (str): The message of the post request, containing some information or error details.

    Returns:
        dict: A dictionary that contains the status and the message of the post request.
    """
    if status == "success":
        logging.info(message)
    else:
        logging.error(message)
    return {
        "status": status,
        "message": message,
    }


class Data(BaseModel):
    movie_id: str


@app.post("/javbus/post/")
def post_movie_info(data: Data) -> dict:
    """
    Find the movie file based on the given movie_id and open it with IINA player.

    Args:
        data (Data): An instance of the data model that contains the movie_id attribute.

    Returns:
        dict: A dictionary that contains the status and the message of the request.

    Raises:
        KeyError: If no movie file is found with the given movie_id.
        CalledProcessError: If the command to open the movie file with IINA fails.
    """
    finder = MovieFinder(MOVIE_DIR)
    finder.find_movies()
    movie_dict = finder.get_movie_dict()
    movie_id = data.movie_id
    movie_path = movie_dict.get(movie_id)
    if movie_path is None:
        error_message = f"No movie found with movie id {movie_id}"
        return log_and_return("error", error_message)
    # Use a context manager to handle subprocess
    with subprocess.Popen(
        ["open", "-a", "IINA", movie_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        # Wait for the process to finish and get the output and error
        _, error = process.communicate()
        if process.returncode == 0:
            error_message = f"Opened {movie_path} with IINA"
            return log_and_return("success", error_message)
        # If the command fails, return an error message
        error_message = f"Failed to open movie with IINA: {error.decode()}"
        return log_and_return("error", error_message)


def run_app_and_observer(source: str):
    """
    Run the observer and the app with a given source.
    """
    finder = MovieFinder(source)
    handler = MovieHandler(finder)
    observer = Observer()
    observer.schedule(handler, source, recursive=True)
    observer.start()
    uvicorn.run(app=app, host="127.0.0.1", port=8082)


if __name__ == "__main__":
    run_app_and_observer(MOVIE_DIR)