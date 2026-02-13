import os
import logging
import time
from pathlib import Path
from typing import Dict, List, Set

IMAGE_EXTENSIONS = (".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp") # lower case in this tuple collection
EXCLUDED_EXTENSIONS = (".ome.tiff.not.used.anymore") # lower case in this tuple collection
EXCLUDED_PREFIXES = ("otf_") # lower case in this tuple collection

MARKER_FILES = ["coordinates.csv", "finished.txt", "done.js"]
def has_marker(path):
    for marker in MARKER_FILES:
        if (Path(path) / marker).exists():
            return True
    return False

def find_dirs_containing_img_files_recursive_from_list_of_paths(path_list: List[str], skip_dirs=None):
    # Normalize skip directories once for quick lookups
    skip_norm: Set[str] = set()
    if skip_dirs:
        for p in skip_dirs:
            if p:
                skip_norm.add(os.path.normpath(str(p).rstrip("/")))

    for path in path_list:
        if not os.path.exists(path):
            logging.exception(f"Path does not exist: {path}")
        else:
            yield from find_dirs_containing_img_files_recursive(path, True, skip_norm)

def find_dirs_containing_img_files_recursive(path: str, sort_dir_entries: bool = False, skip_dirs: Set[str] = None):
    """
    Yield directories that either:
      - Contain at least one image file (matching IMAGE_EXTENSIONS without excluded prefixes/extensions), OR
      - Contain any MARKER_FILES.

    Behavior:
      1. Try os.path.exists(path/marker) for each marker → if found, yield & return immediately.
      2. If no marker found:
         a. Do a single os.scandir(path).
         b. Scan files for the first image-extension match; if found, yield & return (no recursion).
         c. Otherwise, collect subdirectories, sort them if requested, and recurse into each.
      3. Log timing for each major step.
    """
    # Skip directories that are marked as finished to avoid walking them at all
    if skip_dirs:
        norm = os.path.normpath(str(path).rstrip("/"))
        if norm in skip_dirs:
            logging.debug(f"[SKIP  ] Finished dir {path!r}")
            return

    # ── 1) Marker check via os.path.exists() ───────────────────────────────────
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
            logging.debug(
                f"[MARKER] Found {marker!r} in {path!r} "
                f"after {(t_after_exists - t0):.3f}s total"
            )
            yield Path(path)

            single_dir = Path(path) / "single_images"
            if single_dir.exists():
                logging.debug(f"[YIELD ] 'single_images' subdir in {path!r}")
                yield single_dir

            return  # stop processing this folder entirely

    # ── 2) No marker found → one scandir to get entries ─────────────────────────
    t1 = time.perf_counter()
    logging.debug(f"[SCANDIR-START] No marker in {path!r}; scandir to detect files/subdirs")

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

    # ── 2a) Scan files (unsorted) for first image match ─────────────────────────
    found_image = False
    for e in entries:
        if e.name.startswith('.'):
            continue
        if e.is_file(follow_symlinks=False):
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

    # ── 3) If an image was found, yield this directory and return ────────────────
    if found_image:
        logging.debug(f"[YIELD ] {path!r} (image present)")
        yield Path(path)

        single_dir = Path(path) / "single_images"
        if single_dir.exists():
            logging.debug(f"[YIELD ] 'single_images' subdir in {path!r}")
            yield single_dir

        return  # stop processing this folder entirely

    # ── 4) No marker and no image → collect subdirectory paths ───────────────────
    subdir_paths = []
    for e in entries:
        if e.name.startswith('.'):
            continue
        if e.is_dir(follow_symlinks=False):
            subdir_paths.append(e.path)

    # ── 5) Sort subdirectories by descending mtime if requested ────────────────
    if sort_dir_entries and subdir_paths:
        t_sort_start = time.perf_counter()
        try:
            subdir_paths.sort(
                key=lambda sub: os.stat(sub).st_mtime,
                reverse=True
            )
        except Exception as e:
            logging.exception(f"Error sorting subdirs in {path!r}: {e}")
        t_sort_end = time.perf_counter()
        logging.debug(
            f"[SORT-DIRS] Sorted {len(subdir_paths)} subdirs in {path!r} "
            f"in {(t_sort_end - t_sort_start):.3f}s"
        )

    # ── 6) Recurse into subdirectories (possibly sorted) ────────────────────────
    for subdir in subdir_paths:
        logging.debug(f"[RECURSE] Entering subdir: {subdir!r} under parent {path!r}")
        yield from find_dirs_containing_img_files_recursive(subdir, sort_dir_entries, skip_dirs)
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
