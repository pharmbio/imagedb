#!/usr/bin/env python3

class Plate:

  def __init__(self, name):
    self.name = name
    self.timepoints = dict()

  def add(self, timepoint, well, wellsample, channel, img_path):
     self.timepoints.setdefault(timepoint, {})\
                    .setdefault(well, {})\
                    .setdefault(wellsample, []) \
                    .setdefault(channel, []) \
                    .append(img_path)

  def toJson(self):
      timepoints

  def get_timepoint(self, name):
      dict.setdefault("list", []).append("list_item")


class Timepoint:

  def __init__(self, name):
    self.name = name
    self.wells = dict()


class Well:

    def __init__(self, name):
      self.name = name
      self.wellsamples = dict()

class Wellsample:

    def __init__(self, name):
      self.name = name
      self.channels = dict()

class Channel:

    def __init__(self, name):
      self.name = name
      self.path

