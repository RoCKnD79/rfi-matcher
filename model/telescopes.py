import numpy as np
from intervaltree import Interval, IntervalTree

from sopp.custom_dataclasses.facility import Facility
from sopp.custom_dataclasses.coordinates import Coordinates

class Observatory():
    def __init__(self, 
                 name="", 
                 beamwidth=0.0, 
                 elevation=0.0, 
                 latitude=0.0, 
                 longitude=0.0, 
                 declination="7d24m25.426s", 
                 right_ascension="5h55m10.3s",
                 min_freq = 0,
                 max_freq = 0):
        '''
        Parameters
        ----------
        - name: str
        - beamwidth: int
        - elevation: float [m]
        - latitude: float [deg] (North = positive)
        - longitude: float [deg] (East = positive)
        - declination: str 
            ex: "7d24m25.426s"
        - right_ascension: str
            ex: "5h55m10.3s"
        - min_freq: float [MHz]
        - max_freq: float [MHz]
        '''
        self.name = name
        self.beamwidth = beamwidth
        self.elevation = elevation
        self.latitude = latitude
        self.longitude = longitude
        self.declination = declination
        self.right_ascension = right_ascension
        self.freq_interval = Interval(min_freq, max_freq)


HCRO = Observatory("HCRO", 3, 986, 40.8178049, -121.4695413, "7d24m25.426s", "5h55m10.3s", 500, 11000)
MEERKAT = Observatory("MEERKAT", 3, 1309, -30.713333, 21.443056, min_freq=1000, max_freq=10000) # could not find elevation => wrote nearby Carnarvon village's elevation
EVLA = Observatory("EVLA", 3, 2124, 34.078611, 107.617778, min_freq=73, max_freq=50000)
ALMA = Observatory("ALMA", 3, 5058.7, -23.019167, -67.753333, min_freq=31000, max_freq=1e6)