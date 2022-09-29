#!/usr/bin/env python3


class Plate:

    def __init__(self, id):
        self.id = id
        self.acquisitions = dict()

    def add_data(self, image_meta):
        plate_acquisition_id = image_meta['plate_acquisition_id']
        # get or create a new object with this key
        plate_acquisition = self.acquisitions.setdefault(plate_acquisition_id, PlateAcquisition(plate_acquisition_id))
        plate_acquisition.add_data(image_meta)


class PlateAcquisition:

    def __init__(self, id):
        self.id = id
        self.wells = dict()

    def add_data(self, image_meta):
        well_id = image_meta['well']
        # get or create a new object with this key
        well = self.wells.setdefault(well_id, Well(well_id))
        well.add_data(image_meta)


class Well:

    def __init__(self, id):
        self.id = id
        self.sites = dict()

    def add_data(self, image_meta):
        site_id = image_meta['site']
        # get or create a new object with this key
        site = self.sites.setdefault(site_id, Site(site_id))
        site.add_data(image_meta)


class Site:

    def __init__(self, id):
        self.id = id
        self.channels = dict()

    def add_data(self, image_meta):
        channel_id = image_meta['channel']
        channel_dye = image_meta['dye']
        # get or create a new object with this key
        channel = self.channels.setdefault(channel_id, Channel(channel_id, channel_dye))
        channel.add_data(image_meta)


class Channel:

    def __init__(self, id, dye):
        self.id = id
        self.dye = dye
        self.path = ''
        self.image_meta = dict()

    def add_data(self, image_meta):
        self.path = image_meta['path']
        self.image_meta = image_meta

