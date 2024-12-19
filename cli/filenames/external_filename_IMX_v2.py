import re
import os
import logging

def parse_path_and_file(path):

    # If something errors (file not parsable with this parser, then exception and return None)
    try:
        # Example path:
        # /share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s4_w150ACA59D-CE24-4C6D-9A69-55773E3F4DD6.tif

        # First, ensure that "Morphomac" and the plate directory are present
        match = re.search('.*/external-datasets/Morphomac/([^/]+)/', path)
        if match is None:
            logging.debug("Not a Morphomac path.")
            return None

        plate = match.group(1)

        # Now parse the filename part.
        # Pattern we expect in filename (not including path):
        # {plate}_C{well}_s{site}_w{channel}{_thumb}{GUID}.tif
        # where {plate} = something like 2024-W50-Macrophages
        #
        # Example:
        # 2024-W50-Macrophages_C03_s4_w150ACA59D-CE24-4C6D-9A69-55773E3F4DD6.tif
        #                                    ^^^^ GUID starts here
        #
        # We'll break the regex into parts:
        #  - (.+) to capture the plate name again (should match the directory)
        #  - _C([A-Z0-9]{2,3}) to capture well (e.g. C03)
        #  - _s(\d+) to capture site/wellsample
        #  - _w(\d+) to capture the channel number
        #  - (_thumb)? optional thumb
        #  - ([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}) GUID
        #  - \.(tif|tiff|png|jpg|jpeg) extension
        #
        # Note: The plate part in the filename should match the directory plate,
        # but we won't strictly verify equality here unless needed.

        filename = os.path.basename(path)
        pattern = (
            r'^(' + re.escape(plate) + ')'  # plate name captured again for consistency
            + r'_C([A-Z0-9]+)'              # well, e.g. C03
            + r'_s(\d+)'                    # site/wellsample, e.g. s4
            + r'_w(\d+)'                    # channel, e.g. w1
            + r'(_thumb)?'                  # optional thumb
            + r'([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})' # GUID
            + r'\.(tiff?|png|jpe?g)$'       # extension
        )

        match = re.search(pattern, filename, re.IGNORECASE)
        if match is None:
            logging.debug("Filename does not match Morphomac pattern.")
            return None

        # Extract the captured groups
        # group(1): plate in filename
        # group(2): well
        # group(3): site/wellsample
        # group(4): channel
        # group(5): is_thumbnail
        # group(6): GUID
        # group(7): extension

        fname_plate = match.group(1)
        well = match.group(2)
        site = match.group(3)
        channel = match.group(4)
        is_thumbnail = (match.group(5) is not None)
        guid = match.group(6)
        extension = match.group(7)

        valid_extensions = ("tif", "tiff", "png", "jpg", "jpeg")
        if not extension.lower().endswith(valid_extensions):
            logging.debug("Invalid extension.")
            return None

        # Since we have no date in path structure, we set defaults:
        date_year = 2024
        date_month = 1
        date_day_of_month = 1

        metadata = {
            'path': path,
            'filename': filename,
            'date_year': date_year,
            'date_month': date_month,
            'date_day_of_month': date_day_of_month,
            'project': "Morphomac",
            'magnification': '?x',
            'plate': plate,
            'plate_acq_name': path,
            'well': well,
            'wellsample': site,
            'channel': channel,
            'is_thumbnail': is_thumbnail,
            'guid': guid,
            'extension': extension,
            'timepoint': 1,
            'channel_map_id': 1,
            'microscope': "Unknown",
            'parser': os.path.basename(__file__)
        }

        return metadata

    except:
        logging.exception("exception during parsing")
        logging.debug("could not parse filename with this parser")
        return None

if __name__ == '__main__':
    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    # Test with the provided examples
    paths = [
      "/share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s4_w150ACA59D-CE24-4C6D-9A69-55773E3F4DD6.tif",
      "/share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s2_w2_thumb497B52A2-6A42-4806-ADBE-C3194ED71882.tif",
      "/share/data/external-datasets/Morphomac/2024-W50-Macrophages/2024-W50-Macrophages_C03_s1_w20886E4D6-AACE-4092-B1E4-7B951AE4581F.tif"
    ]

    for p in paths:
        retval = parse_path_and_file(p)
        print("\nInput:", p)
        print("Parsed metadata:", retval)
