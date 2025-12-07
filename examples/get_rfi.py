import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import katdal
from skyfield.api import EarthSatellite
from skyfield.timelib import Time

from sopp.custom_dataclasses.satellite.satellite import Satellite

from rfi_matcher.custom.my_tle_fetcher_spacetrack import MyTleFetcherSpacetrack

import matplotlib.pyplot as plt

from rfi_matcher.model.rfi_filter import RaFilter
from rfi_matcher.rfi_matcher import RfiMatcher
from rfi_matcher.utils import sopp_utils, time_utils, skyfield_utils


def main(satellites_filepath=Path('')):

    ra_filter = (
        RaFilter()
            .set_observatories(['MEERKAT'])
            # .set_frequencies([500, 1100])
            # .set_observatories(['VERY LARGE ARRAY NM', 'PARKES NSW', 'MEERKAT'])
            # .set_latitude([-40, 40])
            # .set_longitude([100, 110])
            # .set_frequencies([241000, 275000])
            .set_start_time("2024-06-27T08:49:54.0")
            .set_end_time("2024-06-29T10:32:48.0")
    )

    matcher = RfiMatcher(ra_filter)
    matcher.fetch_tles(satellites_filepath)

    # SCRAPING DATA FROM SELECTED OBSERVATORIES
    observatories = ra_filter.get_observatories()
    observations = matcher.get_all_observations(observatories)
    print("Collected observations:\n", observations)


    # EXTRACTING RFI SOURCES WITH SOPP
    observations_rfi = matcher.extend_observations_with_rfi(observations, lim=10, log=True)
    print("Observations with corresponding satellite RFI sources:\n", observations_rfi)


    # RFI SATELLITE CLOSEST PROXIMITY ESTIMATION
    observations_satprox = matcher.get_all_sat_proximities(observations_rfi)

    # SAVE DATA IN A CSV FILE
    observations_satprox.to_csv('data/rfi_data.csv')


if __name__ == "__main__":

    satellites_filepath = Path('path/to/examples/data')    

    try:
        main(satellites_filepath=satellites_filepath)
    finally:
        satellites_filepath.unlink(missing_ok=True)
        