import os
import logging
from pathlib import Path
from typing import Dict, List

IMAGE_EXTENSIONS = (".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp") # lower case in this tuple collection
EXCLUDED_EXTENSIONS = (".ome.tiff.not.used.anymore") # lower case in this tuple collection
EXCLUDED_PREFIXES = ("otf_") # lower case in this tuple collection

def find_dirs_containing_img_files_recursive_from_list_of_paths(path_list: List[str]):
    for path in path_list:
        if not os.path.exists(path):
            logging.exception(f"Path does not exist: {path}")
        else:
            yield from find_dirs_containing_img_files_recursive(path, True)

def find_dirs_containing_img_files_recursive(path: str, sort_dir_entries: bool = False):
    """
    Yield lowest level directories containing image files as Path (not starting with '.')
    the method is called recursively to find all subdirs
    It breaks the recursion when it finds an image file to avoid looking through all files (long operation)
    """

    if sort_dir_entries:
        iterable_entries = list(os.scandir(path))
        # Sort entries by modification time, most recent first
        iterable_entries.sort(key=lambda e: e.stat().st_mtime, reverse=True)
    else:
        iterable_entries = os.scandir(path)

    for entry in iterable_entries:
        # recurse directories
        if not entry.name.startswith('.') and entry.is_dir():
            yield from find_dirs_containing_img_files_recursive(entry.path)
        if entry.is_file():
            # return parent path if file is imagefile, then break scandir-loop
            if entry.path.lower().endswith( IMAGE_EXTENSIONS ) and not entry.path.lower().endswith( EXCLUDED_EXTENSIONS ):

                parent = Path(entry.path).parent
                yield(parent)
                # A little hack to get subdir "single_images" if it exist, before break looking through this directory
                # check if single_images subdir also exists, if so add that one to
                single_images_dir = parent / "single_images"
                if os.path.exists(single_images_dir):
                    yield single_images_dir

                break

def get_all_image_files(dir):
    # get all files
    logging.info(dir)

    image_files = []
    for file in os.listdir(dir):
        file_lower = file.lower()  # Convert to lower case once to avoid multiple conversions
        if (file_lower.endswith(IMAGE_EXTENSIONS) and
                not (file_lower.endswith(EXCLUDED_EXTENSIONS) or file_lower.startswith(EXCLUDED_PREFIXES))):

            absolute_file = os.path.join(dir, file)
            image_files.append(absolute_file)

    return image_files

def make_thumb_path(image, thumbdir):
    # need to strip / otherwise path can not be joined
    image_subpath = image.strip("/")
    thumb_path = os.path.join(thumbdir, image_subpath)
    return thumb_path