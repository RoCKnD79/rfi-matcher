import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import katdal
from skyfield.api import EarthSatellite
from skyfield.timelib import Time

from sopp.custom_dataclasses.satellite.satellite import Satellite
from sopp.tle_fetcher.tle_fetcher_celestrak import TleFetcherCelestrak
from custom.my_tle_fetcher_spacetrack import MyTleFetcherSpacetrack
# from sopp.tle_fetcher.tle_fetcher_spacetrack import TleFetcherSpacetrack

from model.filter_builder import RaFilter
from model.archive_dictionary import *
from model import sopp_iface
from model import utils

def main(fetch_tles=True, satellites_filepath=Path('')):

    ra_filter = (
        RaFilter()
            .set_observatories(['MEERKAT'])
            # .set_frequencies([500, 1100])
            # .set_observatories(['VERY LARGE ARRAY NM', 'PARKES NSW', 'MEERKAT'])
            # .set_latitude([-40, 40])
            # .set_longitude([100, 110])
            # .set_frequencies([241000, 275000])
            .set_start_time("2025-06-01T08:49:54.0")
            .set_end_time("2025-07-01T10:32:48.0")
    )

    observatories = ra_filter.get_observatories()
    print(observatories)


    if fetch_tles:
        begin = utils.iso_extract_date(ra_filter.startTimeUTC)
        end = utils.iso_extract_date(ra_filter.endTimeUTC)
        print(begin)
        print(end)
        if not satellites_filepath.exists():
            print("Fetching satellite TLEs:", satellites_filepath)
            # TleFetcherCelestrak(satellites_filepath).fetch_tles()
            MyTleFetcherSpacetrack(satellites_filepath, begin, end).fetch_tles()


    # =========================================
    # SCRAPING DATA FROM SELECTED OBSERVATORIES
    # =========================================
    observations = []
    for name in observatories:
        # Fetch the observatory's respective data archive class (given it exists)
        cls = ARCHIVE_CLASSES.get(name)
        if cls is None:
            print(f"Warning: No class defined for {name}")
            continue

        # Instantiate the corresponding data archive object
        archive = cls(ra_filter)
        print(f"Processing {archive.name} with {archive.__class__.__name__}")

        # Fetch the desired observations
        obs_df = archive.get_observations(num=25)
        observations.append(obs_df)

        # Delete the data archive object to free memory
        del archive

    total_obs = pd.concat(observations, ignore_index=True)
    print("Collected observations:\n", total_obs)


    # ================================
    # EXTRACTING RFI SOURCES WITH SOPP
    # ================================

    total_obs = sopp_iface.extend_with_rfi(total_obs, log=True)
    print("Observations with corresponding satellite RFI sources:\n", total_obs)


    # ==========================================
    # RFI SATELLITE CLOSEST PROXIMITY ESTIMATION
    # ==========================================

    for i, obs in total_obs.iterrows():
        # For each observation's potential satellite RFI 
        # => find the position and timestamp where satellite is closest to observation target

        obs_start = obs["begin"]
        obs_end = obs["end"]

        target_ra = utils.ra_str_to_deg(obs["right_ascension"])
        target_dec = utils.dec_str_to_deg(obs["declination"])

        rfi_sat = []
        if obs["NORAD"]:
            for sat in obs["NORAD"]:
                timestamp, ra, dec, ang_dist = utils.sat_proximity(sat, obs_start, obs_end, target_ra, target_dec)
                print("\n=====================")
                print(f"\nObservation | start = {obs_start}, end = {obs_end}")
                print(f"Target | RA = {target_ra}, DEC = {target_dec}")
                      
                print(f"\n--- {sat.name} closest proximity ---")
                print('timestamp:', timestamp)
                print('ra:', ra)
                print('dec:', dec)
                print('ang_dist:', ang_dist)

                rfi_sat.append({
                    "sat": sat.name,
                    "timestamp": timestamp.isoformat(),
                    "declination": float(dec),
                    "right_ascension": float(ra),
                    "angular_distance": float(ang_dist)
                })
            
            total_obs.at[i, "NORAD"] = rfi_sat


    # print(total_obs["NORAD"])
    total_obs.to_csv('/home/rocknd79/EPFL/MA5/SKACH/rfi-matcher/data/rfi_data.csv')


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

    try:
        main(satellites_filepath=satellites_filepath)
    finally:
        #satellites_filepath.unlink(missing_ok=True)
        pass

    #main()
        