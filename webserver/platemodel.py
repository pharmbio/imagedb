class Channel:
    def __init__(self, id, dye):
        self.id = id
        self.dye = dye
        self.path = ''

    def add_data(self, image_meta):
        self.path = image_meta['path']

class Site:
    def __init__(self, id):
        self.id = id
        self.channels = {}

    def get_or_create_channel(self, channel_id, channel_dye):
        # Reducing dictionary lookup by caching the channel object.
        if channel_id not in self.channels:
            self.channels[channel_id] = Channel(channel_id, channel_dye)
        return self.channels[channel_id]

    def add_data(self, image_meta):
        channel = self.get_or_create_channel(image_meta['channel'], image_meta['dye'])
        channel.add_data(image_meta)

class Well:
    def __init__(self, id):
        self.id = id
        self.sites = {}

    def get_or_create_site(self, site_id):
        if site_id not in self.sites:
            self.sites[site_id] = Site(site_id)
        return self.sites[site_id]

    def add_data(self, image_meta):
        site = self.get_or_create_site(image_meta['site'])
        site.add_data(image_meta)

class PlateAcquisition:
    def __init__(self, id):
        self.id = id
        self.wells = {}

    def get_or_create_well(self, well_id):
        if well_id not in self.wells:
            self.wells[well_id] = Well(well_id)
        return self.wells[well_id]

    def add_data(self, image_meta):
        well = self.get_or_create_well(image_meta['well'])
        well.add_data(image_meta)

class Plate:
    def __init__(self, id):
        self.id = id
        self.acquisitions = {}
        self.layout = {}

    def get_or_create_acquisition(self, acquisition_id):
        if acquisition_id not in self.acquisitions:
            self.acquisitions[acquisition_id] = PlateAcquisition(acquisition_id)
        return self.acquisitions[acquisition_id]

    def add_data(self, image_meta):
        acquisition = self.get_or_create_acquisition(image_meta['plate_acquisition_id'])
        acquisition.add_data(image_meta)

    def add_layout(self, layout):
        self.layout = layout