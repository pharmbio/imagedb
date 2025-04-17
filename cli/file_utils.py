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
    Yield lowest‑level dirs that have at least one image.
    •  Scans each directory once (os.scandir).
    •  Stops extension checks after first image, so no per‑file stat() calls later.
    •  Still walks into every sub‑directory.
    """
    entries = list(os.scandir(path))
    if sort_dir_entries:
        entries.sort(key=lambda e: e.stat().st_mtime, reverse=True)

    has_image = False

    # First pass: recurse into sub‑dirs immediately (is_dir may stat once *per subdir*)
    for e in entries:
        if e.name.startswith('.'):
            continue
        # is_dir() might need one stat() per subdir – unavoidable if d_type==UNKNOWN
        if e.is_dir(follow_symlinks=False):
            yield from find_dirs_containing_img_files_recursive(e.path, sort_dir_entries)

    # Second pass: look at files until the first image, then stop
    for e in entries:
        if has_image or e.name.startswith('.') or not e.is_file(follow_symlinks=False):
            continue  # skip hidden, non‑files, and any files after first match
        name_l = e.name.lower()
        if (name_l.endswith(IMAGE_EXTENSIONS) and
            not name_l.endswith(EXCLUDED_EXTENSIONS) and
            not name_l.startswith(EXCLUDED_PREFIXES)):
            has_image = True

    if has_image:
        parent = Path(path)
        yield parent
        single_dir = parent / "single_images"
        if single_dir.exists():
            yield single_dir

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