import os
import re
from datetime import datetime

class Image:

    def __init__(self, meta: dict):
        """
        Initialize the Image wrapper with the given metadata dictionary.
        """
        if not isinstance(meta, dict):
            raise ValueError("meta must be a dictionary")
        self.meta = meta

    @classmethod
    def from_meta(cls, meta: dict):
        """
        Alternate constructor using an existing metadata dictionary.
        """
        return cls(meta)

    def get(self, key, default=None):
        """
        Helper to retrieve a value from the meta dictionary.
        """
        return self.meta.get(key, default)

    def get_path(self):
        return self.get('path')

    def get_plate(self):
        return self.get('plate')

    def get_timepoint(self):
        return self.get('timepoint')

    def get_well(self):
        return self.get('well')

    def get_wellsample(self):
        return self.get('wellsample')

    def get_channel(self):
        return self.get('channel')

    def is_thumbnail(self):
        return self.get('is_thumbnail')

    def get_channel_name(self):
        return self.get('channel_name')

    def get_z(self):
        return self.get('z', 0)

    def get_project(self):
        return self.get('project')

    def get_microscope(self):
        return self.get('microscope')

    def get_channel_map_id(self):
        ## get channel map for speciffic projects/plates
        #specific_ch_map = getChannelMapIDFromMapping(img_meta['project'], img_meta['plate'])
        #if specific_ch_map:
        #    img_meta['channel_map_id'] = specific_ch_map
        return self.get('channel_map_id')

    def get_folder(self):
        # Use provided folder if available; otherwise derive from the path.
        return self.get('folder', os.path.dirname(self.get_path()))

    def get_imaged(self) -> datetime:
        """
        Returns a datetime object for the image's file
        If 'date_iso' is available, it uses that; otherwise falls back to year, month and day.
        """
        date_iso = self.get('date_iso')
        if date_iso:
            return datetime.fromisoformat(date_iso)
        else:
            year = int(self.get('date_year'))
            month = int(self.get('date_month'))
            day = int(self.get('date_day_of_month'))
            return datetime(year, month, day)

    def get_plate_barcode(self) -> str:
        """
        Extracts barcode from the 'plate' field.
        If 'plate' contains a match (e.g., "PB1234"), returns that match.
        Otherwise, returns the plate value unmodified.
        """
        plate = self.get_plate()
        # extract barcode from acquisition_name (if there is one)
        match = re.match(r'(PB?\d+)', plate)
        if match:
            return match.group(1)
        else:
            # return default barcode
            barcode = plate
            return barcode
    def exists_in_db(self) -> bool:
        from database import Database
        return Database.get_instance().image_exists_in_db(self)

    def make_thumb_path(self, thumbdir: str) -> str:
        image_subpath = self.get_path().strip("/")
        thumb_path = os.path.join(thumbdir, image_subpath)
        return thumb_path

    def is_make_thumb(self) -> bool:
        return self.get('make_thumb', True)

    def is_upload_to_s3(self) -> bool:
        excludes = ['/share/data/external-datasets/']

        path = self.get_path()
        if path:
            for exclude in excludes:
                if exclude in path:
                    return False
        return True


    def __str__(self):
        return f"Image(path={self.get_path()}, plate={self.get_plate()}, project={self.get_project()})"
