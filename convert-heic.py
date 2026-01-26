import os
import logging
from PIL import Image
from pillow_heif import register_heif_opener
import tkinter
from tkinter import filedialog

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Prevent an empty tkinter window from appearing
tkinter.Tk().withdraw()


def convert_files(files: list) -> None:
    """Iterates through a list of files and converts them to JPG format and saves them in the same directory."""

    for file in files:
        img = Image.open(file)
        destFilePath = os.path.splitext(file)[0] + ".jpg"
        img.save(destFilePath, "JPEG")
        logging.info(f"{file} converted to {destFilePath}")


def convert_folder(inputFolder) -> None:
    """Converts all HEIC files in a folder to JPG format."""

    for file in os.listdir(inputFolder):
        # Skip if not a HEIC file
        if not file.lower().endswith(".heic"):
            logging.info(f"{file} is not a HEIC file. Skipping...")
            continue

        filePath = os.path.join(inputFolder, file)
        destFilePath = os.path.join(inputFolder, "converted_jpgs")

        if not os.path.exists(destFilePath):
            os.makedirs(destFilePath)

        output_file = os.path.join(destFilePath, os.path.splitext(file)[0] + ".jpg")
        img = Image.open(filePath.replace("\\", "/"))
        img.save(output_file, "JPEG")
        logging.info(f"{file} converted to {output_file}")

    logging.info("Conversion complete.")


def main():
    """Main function that asks user for input and handles files and folders."""
    register_heif_opener()  # Register the HEIF file format with PIL

    print(
"""
=====================================
HEIC to JPG Converter
====================================="""
    )

    while True:
        input_type = input(
"""Choose an option on how to select HEIC files to convert:

    1. Select a folder containing HEIC files
    2. Select individual HEIC files

Type 'exit' or 'quit' to close the program. \n > """ 
)
        print(input_type, type(input_type))
        match input_type.lower():
            case "1":
                try:
                    folder = filedialog.askdirectory(
                        title="Select folder containing HEIC files to convert."
                    )
                    convert_folder(folder)
                except FileNotFoundError:
                    logging.info("Folder not found. Please try again.")
                    continue
                break
            case "2":
                files = filedialog.askopenfilenames(
                    title="Select HEIC files to convert."
                )
                convert_files(files)
                break
            case "exit":
                break
            case "quit":
                break
            case _:
                logging.info("Invalid input.")
                continue

    input("\nPress enter to exit.")
    exit()


if __name__ == "__main__":
    main()
