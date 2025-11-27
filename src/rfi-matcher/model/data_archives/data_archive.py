from abc import ABC, abstractmethod

from urllib.request import urlopen
import json
import pandas as pd

from ..filter_builder import RaFilter

class DataArchive(ABC):
    required_attributes = ["name", "latitude", "longitude", "elevation"]

    def __init_subclass__(cls):
        super().__init_subclass__()

        # Enforce required class-level attributes
        for attr in cls.required_attributes:
            if not hasattr(cls, attr):
                raise TypeError(
                    f"Subclass '{cls.__name__}' must define attribute '{attr}'"
                )

    @abstractmethod
    def get_observations(self, num: int) -> pd.DataFrame:
        pass 


    def get_df_order(self):
        return ["name", "observation_id", "frequency", "bandwidth", "declination", "right_ascension", "begin", "end", "url"]


    def get_html(self, url):
        '''
        Returns json data read from the url given in parameter    
        '''
        page = urlopen(url)

        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

        return json.loads(html)


    def freq_to_bands(self, freq_min, freq_max):
        """
        Returns the astronomy band(s) overlapping with the given frequency range.
        
        freq_min_mhz: Minimum frequency in MHz
        freq_max_mhz: Maximum frequency in MHz
        
        Returns a list of band names.
        """
        
        # Standard radio astronomy bands (in MHz)
        bands = {
            "HF": (3, 30),
            "VHF": (30, 300),
            "ULF": (300, 1000),
            "L":  (1000, 2000),
            "S":  (2000, 4000),
            "C":  (4000, 8000),
            "X":  (8000, 12000),
            "Ku": (12000, 18000),
            "K":  (18000, 27000),
            "Ka": (27000, 40000),
            "Q":  (33000, 50000),
            "V":  (50000, 75000),
            "W":  (75000, 110000)
        }
        
        overlapping_bands = []
        
        for band, (band_min, band_max) in bands.items():
            # Check if the input range overlaps with this band
            if freq_min <= band_max and freq_max >= band_min:
                overlapping_bands.append(band)
        
        return overlapping_bands