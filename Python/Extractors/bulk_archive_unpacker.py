"""
Bulk Archive Unpacker
"""

import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class BulkArchiveUnpacker:
    def __init__(self, directory_path, output_directory, max_workers=4):
        self.directory_path = Path(directory_path)
        self.output_directory = Path(output_directory)
        self.max_workers = max_workers

        # Configure logging to record extraction process
        logging.basicConfig(
            filename="extract_log.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def extract_archive(self, archive):
        try:
            output_path = (
                self.output_directory / archive.stem
            )  # Create an output folder named after the archive
            output_path.mkdir(parents=True, exist_ok=True)

            # Use 'unar' to extract files; '-q' ensures no overwriting prompts or manual interaction
            subprocess.run(
                ["unar", "-q", "-p", "", str(archive), "-o", str(output_path)],
                check=True,
                stderr=subprocess.PIPE,
            )

        except subprocess.CalledProcessError as e:
            logging.error(
                f"Failed to extract {archive}: {e.stderr.decode('utf-8', 'ignore')}"
            )

    def extract_all_archives(self):
        # Find all archive files with supported extensions
        archives = [
            file
            for file in self.directory_path.rglob("*")
            if file.suffix in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]
        ]

        # Use multithreading to extract archives in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.extract_archive, archives)


if __name__ == "__main__":
    directory_path = (
        "/Volumes/YYeTs_20_Years_Subtitles/Backup"  # Path to archive directory
    )
    output_directory = (
        "/Volumes/YYeTs_20_Years_Subtitles/Extracted"  # Path for extracted files
    )

    # Initialize and run the unpacker
    unpacker = BulkArchiveUnpacker(directory_path, output_directory, max_workers=8)
    unpacker.extract_all_archives()
