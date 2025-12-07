from pathlib import Path
import datetime

import pandas as pd
import numpy as np

from sopp.custom_dataclasses.satellite.satellite import Satellite

from rfi_matcher.custom.my_tle_fetcher_spacetrack import MyTleFetcherSpacetrack
from rfi_matcher.model.rfi_filter import RaFilter
from rfi_matcher.utils import sopp_utils, skyfield_utils, time_utils
from rfi_matcher.model.archive_dictionary import ARCHIVE_CLASSES


class RfiMatcher:

    def __init__(self, ra_filter: RaFilter = RaFilter()):
        self.ra_filter = ra_filter
        save_dir = Path('')


    def fetch_tles(self, satellites_filepath: str = 'data/satellites.tle'):
        ra_filter = self.ra_filter

        begin = time_utils.iso_extract_date(ra_filter.startTimeUTC)
        end = time_utils.iso_extract_date(ra_filter.endTimeUTC)
        print(begin)
        print(end)
        
        satellites_filepath = Path(satellites_filepath)
        if not satellites_filepath.exists():
            print("Fetching satellite TLEs:", satellites_filepath)
            MyTleFetcherSpacetrack(satellites_filepath, begin, end).fetch_tles()


    def get_all_observations(self, observatories: list[str]) -> pd.DataFrame:
        observations = []

        for name in observatories:
            print(f"Fetching from {name}")
            obs_df = self.get_observations_for(name)
            observations.append(obs_df)

        df = pd.concat(observations, ignore_index=True)
        return df
    

    def get_observations_for(self, observatory: str) -> pd.DataFrame:

        cls = ARCHIVE_CLASSES.get(observatory)
        if cls is None:
            print(f"Warning: No class defined for {observatory}")

        # Instantiate the corresponding data archive object
        archive = cls(self.ra_filter)

        # Fetch the desired observations
        obs_df = archive.get_observations(num=25)

        # Delete the data archive object to free memory
        del archive

        return obs_df


    def extend_observations_with_rfi(self, observations: pd.DataFrame, lim=None, log=False):
        total_obs = observations.copy()
        total_obs["NORAD"] = None

        if lim == None: 
            lim = total_obs.shape[0]
        
        for i, obs in total_obs.iterrows():
            if(i > lim): break

            begin = obs['begin']
            end = obs['end']

            begin = time_utils.iso_to_datetime(begin)
            end = time_utils.iso_to_datetime(end)

            if log:
                print(f"\nprocessing row: {i} | begin: {begin}, end: {end}")


            if(begin >= end):
                rfi = []
            else:
                rfi = sopp_utils.get_rfi_sources(obs)
            total_obs.at[i, "NORAD"] = rfi

            if log:
                print(f'Found: {sopp_utils.get_rfi_names(rfi)}')

        return total_obs
    


    def get_all_sat_proximities(self, total_observations: pd.DataFrame):
        total_obs = total_observations.copy()
        for i, obs in total_obs.iterrows():
            # For each observation's potential satellite RFI 
            # => find the position and timestamp where satellite is closest to observation target

            obs_start = obs["begin"]
            obs_end = obs["end"]

            target_ra = skyfield_utils.ra_str_to_deg(obs["right_ascension"])
            target_dec = skyfield_utils.dec_str_to_deg(obs["declination"])

            rfi_sat = []
            if obs["NORAD"]:
                for sat in obs["NORAD"]:
                    timestamp, ra, dec, ang_dist = skyfield_utils.sat_proximity(sat, obs_start, obs_end, target_ra, target_dec)
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

        return total_obs