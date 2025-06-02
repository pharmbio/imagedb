import os
import logging
import time
from pathlib import Path
from typing import Dict, List

IMAGE_EXTENSIONS = (".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp") # lower case in this tuple collection
EXCLUDED_EXTENSIONS = (".ome.tiff.not.used.anymore") # lower case in this tuple collection
EXCLUDED_PREFIXES = ("otf_") # lower case in this tuple collection

MARKER_FILES = ["coordinates.csv", "finished.txt", "done.js"]
def has_marker(path):
    for marker in MARKER_FILES:
        if (Path(path) / marker).exists():
            return True
    return False

def find_dirs_containing_img_files_recursive_from_list_of_paths(path_list: List[str]):
    for path in path_list:
        if not os.path.exists(path):
            logging.exception(f"Path does not exist: {path}")
        else:
            yield from find_dirs_containing_img_files_recursive(path, True)

def find_dirs_containing_img_files_recursive(path: str, sort_dir_entries: bool = False):
    """
    Yield directories that either:
      - Contain at least one image file (matches IMAGE_EXTENSIONS without excluded prefixes/extensions), OR
      - Contain any MARKER_FILES.

    This version:
      1. Tries os.path.exists(path/marker) for each marker → if found, yield & return.
      2. Only if no marker was found, does a single os.scandir(path):
         • Gather subdirectories to recurse into.
         • Stop at the first image-extension match, yield & continue recursion.
      3. Logs timing at every major step.
    """
    # ── 1) Try each marker via direct os.path.exists() ─────────────────────────
    t0 = time.perf_counter()
    for marker in MARKER_FILES:
        marker_path = os.path.join(path, marker)
        t_check = time.perf_counter()
        exists = os.path.exists(marker_path)
        t_after_exists = time.perf_counter()
        logging.debug(
            f"[EXISTS] Checked marker {marker!r} in {path!r} "
            f"in {(t_after_exists - t_check):.3f}s → {exists}"
        )
        if exists:
            # We found a marker; yield and immediately return (no further scans in this folder)
            logging.debug(
                f"[MARKER] Found {marker!r} in {path!r} "
                f"after {(t_after_exists - t0):.3f}s total"
            )
            yield Path(path)

            # If a "single_images" subfolder exists, yield that too (but still no deeper recursion here)
            single_dir = Path(path) / "single_images"
            if single_dir.exists():
                logging.debug(f"[YIELD ] 'single_images' subdir in {path!r}")
                yield single_dir

            # Stop processing this folder altogether
            return

    # ── 2) No marker found → list directory once to look for images & subdirs ───
    t1 = time.perf_counter()
    logging.debug(f"[SCANDIR-START] No marker in {path!r}, now scandir to detect images/subdirs")

    try:
        entries = list(os.scandir(path))
    except Exception as e:
        logging.exception(f"Could not scandir {path!r}: {e}")
        return

    t2 = time.perf_counter()
    logging.debug(
        f"[SCANDIR-END] Retrieved {len(entries)} DirEntry objects in {path!r} "
        f"in {(t2 - t1):.3f}s"
    )

    subdirs = []
    found_image = False

    for e in entries:
        # skip hidden names immediately
        if e.name.startswith('.'):
            continue

        if e.is_dir(follow_symlinks=False):
            subdirs.append(e.path)
        elif e.is_file(follow_symlinks=False):
            name_l = e.name.lower()
            if (
                name_l.endswith(IMAGE_EXTENSIONS)
                and not name_l.endswith(EXCLUDED_EXTENSIONS)
                and not name_l.startswith(EXCLUDED_PREFIXES)
            ):
                found_image = True
                t_img = time.perf_counter()
                logging.debug(
                    f"[IMAGE ] Found image {e.name!r} in {path!r} "
                    f"after {(t_img - t2):.3f}s since scandir"
                )
                break

    # ── 3) If an image was found, yield this directory ─────────────────────────
    if found_image:
        logging.debug(f"[YIELD ] {path!r} (image present)")
        yield Path(path)

        single_dir = Path(path) / "single_images"
        if single_dir.exists():
            logging.debug(f"[YIELD ] 'single_images' subdir in {path!r}")
            yield single_dir

    # ── 4) Recurse into each subdirectory (only now) ───────────────────────────
    for subdir in subdirs:
        logging.debug(f"[RECURSE] Entering subdir: {subdir!r} under parent {path!r}")
        yield from find_dirs_containing_img_files_recursive(subdir, sort_dir_entries)
        logging.debug(f"[RETURN ] Back from subdir: {subdir!r} to parent {path!r}")


def find_dirs_containing_img_files_recursive_old(path: str, sort_dir_entries: bool = False):
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