#!/usr/bin/env python3
"""
Generic Christa‑style upload parser

Folder layout
─────────────
…/external-datasets/<project>/<plate_acq_name>/YYYY-MM-DD/<plate_id>/
    TimePoint_<t>/[ZStep_<z>/] <filename>.tif[f]
"""

import re
import os
import logging
from pathlib import Path
from datetime import datetime

def get_folder(file_path: str) -> str:
    """
    Return the absolute dir that ends with “TimePoint” or full dir if not found
    """

    p = Path(file_path).resolve()

    # Walk up until we find a parent whose name starts with "TimePoint_"
    for parent in p.parents:
        if parent.name.startswith("TimePoint"):
            return str(parent)
    # Fallback: just return the immediate directory
    return str(p.parent) + os.sep

def parse_path_and_file(path: str):
    """Return a metadata dict, or None if path doesn’t match expected pattern."""
    try:
        # ── 1.  parse folder structure ───────────────────────────────────────
        m = re.match(
            r""".*/external-datasets/christa-patient-painting/   # ← project
                (?P<plate_acq_name>[^/]+)/          # ← experiment / plate‑acq‑name
                (?P<date>\d{4}-\d{2}-\d{2})/        # YYYY‑MM‑DD
                (?P<plate_id>\d+)/                  # numeric plate id
                TimePoint_(?P<timepoint>\d+)        # TimePoint_n
                (?:/ZStep_(?P<z>\d+))?              # optional ZStep_z
                / .*                                # rest of path
            """,
            path,
            re.VERBOSE,
        )
        if not m:
            logging.debug("Folder pattern did not match")
            return None

        project         = "christa-patient-painting"         # folder after /upload/
        plate_acq_name  = m.group("plate_acq_name")
        date_str        = m.group("date")
        plate_id        = m.group("plate_id")
        timepoint       = int(m.group("timepoint"))
        z               = int(m.group("z") or 0)

        dt = datetime.strptime(date_str, "%Y-%m-%d")

        # ── 2.  parse filename ───────────────────────────────────────────────
        fm = re.match(
            r"""
              .*/                                   # path up to last “/”
              (?:.*?_)?                             # optional prefix
              (?P<well>[A-Z]{1,2}\d+)               # well (A1 … AA24 …)
              _s(?P<site>\d+)                       # site
              _w(?P<channel>\d+)                    # channel
              (?P<thumb>_thumb)?                    # optional _thumb
              (?P<guid>[A-F0-9\-]{36})?             # optional UUID
              \.(?P<ext>[^.]+)$                     # extension
            """,
            path,
            re.VERBOSE | re.IGNORECASE,
        )
        if not fm:
            logging.debug("Filename pattern did not match")
            return None

        well        = fm.group("well")
        site        = int(fm.group("site"))
        channel     = int(fm.group("channel"))
        is_thumb    = fm.group("thumb") is not None
        guid        = fm.group("guid") or "no-guid"
        extension   = fm.group("ext")

        folder = get_folder(path)

        if extension.lower() not in ("tif", "tiff", "png", "jpg", "jpeg"):
            logging.debug("Unsupported extensionrc")
            return None

        # ── 3.  build metadata dict ─────────────────────────────────────────
        return {
            "path":              path,
            "folder":            folder,
            "filename":          os.path.basename(path),
            "date_year":         dt.year,
            "date_month":        dt.month,
            "date_day_of_month": dt.day,
            "project":           project,           # from folder after /upload/
            "magnification":     "?x",
            "plate":             plate_id,          # numeric id
            "plate_acq_name":    plate_acq_name,    # experiment folder
            "well":              well,
            "wellsample":        site,
            "z":                 z,
            "channel":           channel,
            "channel_name":      str(channel),
            "is_thumbnail":      is_thumb,
            "guid":              guid,
            "extension":         extension,
            "timepoint":         timepoint,
            "channel_map_id":    37,
            "microscope":        "Unknown",
            "make_thumb":        "False",
            "parser":            os.path.basename(__file__),
        }

    except Exception:
        logging.exception("Exception while parsing")
        return None


# ── stand‑alone quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )

    test_paths = [
        "/share/data/external-datasets/christa-patient-painting/CRC-104-Growdex-10X-stained/2025-03-14/25468/TimePoint_1/ZStep_20/CRC-104-Growdex-10X-stained_O18_s3_w1BDD61EF7-D950-46CE-8A55-EBC514171E41.tif",
        "/share/data/external-datasets/christa-patient-painting/CRC-104-Growdex-10X-stained/2025-03-14/25468/TimePoint_1/CRC-104-Growdex-10X-stained_M14_s2_w17233047D-1F31-4056-B84E-1985B8F85088.tif",
    ]

    for p in test_paths:
        print("\n", parse_path_and_file(p))
