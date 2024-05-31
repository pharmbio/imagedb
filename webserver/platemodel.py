from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Channel:
    id: int
    dye: str
    path: str = ''

    def add_data(self, image_meta):
        self.path = image_meta['path']

@dataclass
class Zpos:
    z_value: int
    channels: Dict[int, Channel] = field(default_factory=dict)

    def get_or_create_channel(self, channel_id, channel_dye):
        if channel_id not in self.channels:
            self.channels[channel_id] = Channel(channel_id, channel_dye)
        return self.channels[channel_id]

    def add_data(self, image_meta):
        channel = self.get_or_create_channel(image_meta['channel'], image_meta['dye'])
        channel.add_data(image_meta)

@dataclass
class Site:
    id: int
    z_positions: Dict[int, Zpos] = field(default_factory=dict)

    def get_or_create_z_position(self, z_value):
        if z_value not in self.z_positions:
            self.z_positions[z_value] = Zpos(z_value)
        return self.z_positions[z_value]

    def add_data(self, image_meta):
        z_position = self.get_or_create_z_position(image_meta['z'])
        z_position.add_data(image_meta)

@dataclass
class Well:
    id: int
    sites: Dict[int, Site] = field(default_factory=dict)

    def get_or_create_site(self, site_id):
        if site_id not in self.sites:
            self.sites[site_id] = Site(site_id)
        return self.sites[site_id]

    def add_data(self, image_meta):
        site = self.get_or_create_site(image_meta['site'])
        site.add_data(image_meta)

@dataclass
class PlateAcquisition:
    id: int
    project: str
    name: str
    folder: str
    wells: Dict[int, Well] = field(default_factory=dict)

    def get_or_create_well(self, well_id):
        if well_id not in self.wells:
            self.wells[well_id] = Well(well_id)
        return self.wells[well_id]

    def add_data(self, image_meta):
        well = self.get_or_create_well(image_meta['well'])
        well.add_data(image_meta)

@dataclass
class Plate:
    id: int
    acquisitions: Dict[int, PlateAcquisition] = field(default_factory=dict)
    layout: Dict = field(default_factory=dict)

    def get_or_create_acquisition(self, acquisition_id, project, name, folder):
        if acquisition_id not in self.acquisitions:
            self.acquisitions[acquisition_id] = PlateAcquisition(acquisition_id, project, name, folder)
        return self.acquisitions[acquisition_id]

    def add_data(self, image_meta):
        acquisition = self.get_or_create_acquisition(image_meta['plate_acquisition_id'], image_meta['project'], image_meta['plate_acquisition_name'], image_meta['folder'])
        acquisition.add_data(image_meta)

    def add_layout(self, layout):
        self.layout = layout