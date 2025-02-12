import subprocess
from pathlib import Path


class DdrescueSync:
    """
    Class responsible for synchronizing files from a source directory to a target directory
    using ddrescue for recovery and file synchronization.
    """

    def __init__(self, source_directory, target_directory):
        """
        Initialize the DdrescueSync object with source and target directories.

        Args:
            source_directory (str): Path to the source directory.
            target_directory (str): Path to the target directory.
        """
        self.source_directory = Path(source_directory)
        self.target_directory = Path(
            target_directory
        ).joinpath(
            self.source_directory.name  # Append the source directory name to the target path
        )
        # Ensure the target directory exists, create it if necessary
        self.target_directory.mkdir(parents=True, exist_ok=True)

    def sync_directories(self):
        """
        Synchronize files and directories from the source to the target directory.

        It will copy files using ddrescue and remove the source files after successful sync.
        """
        # Iterate over all files and directories in the source directory recursively
        for source_path in self.source_directory.rglob("*"):
            if (
                ".DS_Store" in source_path.name
            ):  # Skip hidden system files (MacOS specific)
                continue
            relative_path = source_path.relative_to(
                self.source_directory
            )  # Get the relative path
            target_path = (
                self.target_directory / relative_path
            )  # Corresponding target path

            if (
                source_path.is_file() and not target_path.is_file()
            ):  # If it's a file and not yet synced
                self.create_directory(
                    target_path.parent
                )  # Ensure the target directory exists
                self.sync_and_remove(
                    source_path, target_path
                )  # Sync the file and remove the source
            elif (
                source_path.is_dir()
            ):  # If it's a directory, ensure it exists in the target
                self.create_directory(target_path)

    def sync_and_remove(self, source_file: Path, target_file: Path):
        """
        Synchronize a single file using ddrescue and remove the source file after successful sync.

        Args:
            source_file (Path): Path to the source file.
            target_file (Path): Path to the target file.
        """
        # Use ddrescue command to sync the files (with options for recovery and speed)
        command = [
            "ddrescue",
            "-r0",  # Retry level
            "-n",  # No split option, skip bad blocks
            str(source_file),
            str(target_file),
        ]
        try:
            # Run the ddrescue command and check for errors
            subprocess.run(command, check=True)
            # print(f"Synced: {source_file} -> {target_file}")
            self.remove_source(source_file)  # Remove the source file after syncing
        except subprocess.CalledProcessError as e:
            # Handle errors during the syncing process
            print(f"Error syncing {source_file}: {e}")

    def create_directory(self, target_directory):
        """
        Create the target directory if it doesn't already exist.

        Args:
            target_directory (Path): Path to the target directory to create.
        """
        try:
            # Create the target directory if it doesn't exist
            target_directory.mkdir(parents=True, exist_ok=True)
            # print(f"Created directory: {target_directory}")
        except Exception as e:
            # Handle errors while creating directories
            print(f"Error creating directory {target_directory}: {e}")

    def remove_source(self, source_file: Path):
        """
        Remove the source file after it has been successfully synced.

        Args:
            source_file (Path): Path to the source file to be removed.
        """
        try:
            if source_file.is_file():
                # Remove the source file after syncing
                source_file.unlink()
            # print(f"Removed source file: {source_file}")
        except Exception as e:
            # Handle errors while removing the source file
            print(f"Error removing source file {source_file}: {e}")


# Source and target directory paths
source_directory = "/Volumes/WD_5TB/"
target_directory = "/Users/m/Downloads/backup_files"

# Initialize the DdrescueSync object and perform the sync
syncer = DdrescueSync(source_directory, target_directory)
syncer.sync_directories()
