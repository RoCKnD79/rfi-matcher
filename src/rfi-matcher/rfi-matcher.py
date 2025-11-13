import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import katdal

from sopp.tle_fetcher.tle_fetcher_celestrak import TleFetcherCelestrak

from model.filter_builder import RaFilter
from model.archive_dictionary import *
from model.utils import get_rfi_sources

def main():
    ra_filter = (
        RaFilter()
            .set_observatories(['MEERKAT'])
            .set_frequencies([500, 1100])
            # .set_observatories(['VERY LARGE ARRAY NM', 'PARKES NSW', 'MEERKAT'])
            # .set_latitude([-40, 40])
            # .set_longitude([100, 110])
            # .set_frequencies([241000, 275000])
    )

    observatories = ra_filter.get_observatories()
    print(observatories)

    # Iterate over filtered observatories
    observations = []
    for name in observatories:
        cls = ARCHIVE_CLASSES.get(name)
        if cls is None:
            print(f"Warning: No class defined for {name}")
            continue

        # Instantiate the corresponding data archive object
        archive = cls(ra_filter)

        # Fetch the desired observations
        obs_df = archive.get_observations()
        # print(obs_df)
        print(f"Processing {archive.name} with {archive.__class__.__name__}")

        observations.append(obs_df)

        # Delete the data archive object to free memory
        del archive

    total_obs = pd.concat(observations, ignore_index=True)
    print(total_obs)

    total_obs["NORAD"] = None

    for i, obs in total_obs.iterrows():
        print('\nprocessing row', i)
        rfi = get_rfi_sources(obs)
        total_obs.at[i, "NORAD"] = rfi

    print(total_obs)


    # ---- KATDAL TEST ----
    # print(total_obs.iloc[0]["url"])
    # d = katdal.open(total_obs.iloc[0]["url"])
    # d.select(scans='track', channels=slice(200, 300), ants='m000')
    # print(d)

    # plt.plot(d.az, d.el, 'o')
    # plt.xlabel('Azimuth (degrees)')
    # plt.ylabel('Elevation (degrees)')
    # plt.show()


if __name__ == "__main__":

    satellites_filepath = Path('/home/rocknd79/EPFL/MA5/SKACH/rfi-matcher/data/satellites.tle')
    if not satellites_filepath.exists():
        print("Fetching satellite TLEs:", satellites_filepath)
        TleFetcherCelestrak(satellites_filepath).fetch_tles()

    try:
        main()
    finally:
        satellites_filepath.unlink(missing_ok=True)

    # main()
        