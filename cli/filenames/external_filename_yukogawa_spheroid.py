import re
import os
import logging

def parse_path_and_file(path):
    """
    Parses a full path like:
      /share/data/external-datasets/spher-colo52-az/
         CellPainting_cellpainttestwithBOMI_20241028_132131/
         AssayPlate_Corning_3830/
         AssayPlate_Corning_3830_G16_T0001F001L01A05Z40C05.tif

    Returns a metadata dict, or None if the file doesn't match.
    """

    try:
        # ---------------------------------------------------------------------
        # 1) Extract 'project', 'experiment', and 'plate' from the path
        #    Example capturing:
        #      project    = "spher-colo52-az"
        #      experiment = "CellPainting_cellpainttestwithBOMI_20241028_132131"
        #      plate      = "AssayPlate_Corning_3830"
        # ---------------------------------------------------------------------
        match = re.search(
            r'^.*/external-datasets/(?P<project>[^/]+)/(?P<experiment>[^/]+)/(?P<plate>AssayPlate_Corning_[0-9]+)/',
            path
        )
        if match is None:
            return None

        project    = match.group('project')     # e.g. "spher-colo52-az"
        experiment = match.group('experiment')  # e.g. "CellPainting_cellpainttestwithBOMI_20241028_132131"
        plate      = match.group('plate')       # e.g. "AssayPlate_Corning_3830"

        if project != "spher-colo52-az":
            return None

        logging.debug(f"project: {project}")
        logging.debug(f"experiment: {experiment}")
        logging.debug(f"plate: {plate}")

        match = re.search(
            r'.*/(AssayPlate_Corning_[0-9]+)_([A-Z]\d{2})_'  # e.g. ..._G16_
            r'T([0-9]+)'                                     # T0001
            r'F([0-9]+)'                                     # F001
            r'L([0-9]+)'                                     # L01
            r'A([0-9]+)'                                     # A05
            r'Z([0-9]+)'                                     # Z40
            r'C([0-9]+)\.'                                   # C05.
            r'(.*)$',                                        # extension
            path
        )
        logging.debug(f"match: {match}")

        if match is None:
            return None

        # We won't store the plate from group(1) again, since we already captured it above
        well       = match.group(2)  # e.g. "G16"
        timepoint  = int(match.group(3))  # e.g. 1
        site       = int(match.group(4))  # e.g. 1
        # group(5) => L index (not stored in metadata, but parsed if needed)
        # group(6) => A index (not stored in metadata)
        z          = int(match.group(7))      # e.g. 40
        channel    = int(match.group(8))      # e.g. 5
        extension  = match.group(9).lower()   # e.g. "tif"

        # Return if wrong extension
        valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg") # Needs to be tuple, not list
        if not extension.lower().endswith( valid_extensions ):
            logging.debug("no extension")
            return None

        # ---------------------------------------------------------------------
        # 4) Build the metadata dictionary
        #    We provide placeholder date values, microscope, etc.
        # ---------------------------------------------------------------------
        metadata = {
            'path': path,
            'filename': os.path.basename(path),
            'date_year': 2024,
            'date_month': 10,
            'date_day_of_month': 1,
            'project': project,
            'magnification': '?x',
            'plate': plate,
            'plate_acq_name': path,
            'well': well,
            'wellsample': site,
            'channel': channel,
            'z': z,
            'is_thumbnail': False,
            'guid': None,
            'extension': extension,
            'timepoint': timepoint,
            'channel_map_id': 36,
            'microscope': "Yukogawa",
            'experiment': experiment,
            'parser': os.path.basename(__file__),
        }

        return metadata

    except Exception:
        logging.exception("exception")
        logging.debug("could not parse")
        return None


if __name__ == '__main__':
    #
    # Configure logging
    #
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )

    # Test parse
    test_paths = [
        "/share/data/external-datasets/spher-colo52-az/CellPainting_cellpainttestwithBOMI_20241028_132131/AssayPlate_Corning_3830/AssayPlate_Corning_3830_G16_T0001F001L01A05Z40C05.tif",
        "/share/data/external-datasets/spher-colo52-az/CellPainting_20241220clearedspheroidsBOMI_20241220_151510/AssayPlate_Corning_3830/AssayPlate_Corning_3830_F16_T0001F001L01A04Z58C04.tif",
        "/share/data/external-datasets/spher-colo52-az/CellPainting_20241220clearedspheroidsBOMI_20241220_151510/AssayPlate_Corning_3830/AssayPlate_Corning_3830_I02_T0001F001L01A01Z01C01.tif",
        "/share/data/external-datasets/spher-colo52-az/CellPainting_20250127Cellpaintcleared3D_20250127_171120/AssayPlate_Corning_3830/AssayPlate_Corning_3830_H23_T0001F001L01A05Z62C05.tif"
    ]

    for test_path in test_paths:
        retval = parse_path_and_file(test_path)
        print(f"\nretval for {test_path} = {retval}")




