import pandas as pd
from .data_archive import DataArchive
from model.filter_builder import RaFilter

class MeerkatDataArchive(DataArchive):

    def __init__(self, ra_filter: RaFilter):
        self.name = "MeerKAT"
        self.ra_filter = ra_filter

    def get_observations(self):
        pass
