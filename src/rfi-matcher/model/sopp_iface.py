import pandas as pd
from pathlib import Path

from sopp.sopp import Sopp
from sopp.custom_dataclasses.satellite.satellite import Satellite
from sopp.builder.configuration_builder import ConfigurationBuilder
from sopp.tle_fetcher.tle_fetcher_celestrak import TleFetcherCelestrak

from model.archive_dictionary import *

def get_rfi_sources(df_obs: pd.DataFrame, mainbeam=True) -> list[Satellite]:
    '''
    scope = 0 (satellites crossing mainbeam)
    scope = 1 (all satellites above horizon)
    '''

    name = df_obs['name']
    archive = ARCHIVE_CLASSES.get(name)
    lat = archive.latitude
    lon = archive.longitude
    el = archive.elevation

    configuration = (
        ConfigurationBuilder()
        .set_facility(
            latitude=lat,
            longitude=lon,
            elevation=el,
            name=name,
            beamwidth=3,
        )
        .set_frequency_range(
            bandwidth=df_obs['bandwidth'],
            frequency=df_obs['frequency']
        )
        .set_time_window(
            begin=df_obs['begin'],
            end=df_obs['end']
        )
        .set_observation_target(
            declination=df_obs["declination"],
            right_ascension=df_obs["right_ascension"]
        )
        .set_runtime_settings(
            concurrency_level=8,
            time_continuity_resolution=1,
            min_altitude=5.0,
        )
        # Alternatively set all of the above settings from a config file
        #.set_from_config_file(config_file='./supplements/config.json')
        .set_satellites(tle_file='/home/rocknd79/EPFL/MA5/SKACH/rfi-matcher/data/satellites.tle', frequency_file='/home/rocknd79/EPFL/MA5/SKACH/rfi-matcher/data/satellite_frequencies.csv')
        .build()
    )

    sopp_obj = Sopp(configuration)

    if mainbeam:
        rfi_overhead = sopp_obj.get_satellites_crossing_main_beam()
    else:
        rfi_overhead = sopp_obj.get_satellites_above_horizon()

    rfi_satellites = []
    for sat in rfi_overhead:
        rfi_satellites.append(sat.satellite)

    return rfi_satellites


def get_rfi_names(satellites: list[Satellite]) -> list[str]:
    names = []
    for sat in satellites:
        names.append(sat.name)
    
    return names


def extend_with_rfi(observations: pd.DataFrame, log=False):
    total_obs = observations.copy()
    total_obs["NORAD"] = None

    for i, obs in total_obs.iterrows():
        if(i > 1): break

        if log:
            begin = obs['begin']
            end = obs['end']
            print(f"\nprocessing row: {i} | begin: {begin}, end: {end}")
        
        rfi = get_rfi_sources(obs)
        total_obs.at[i, "NORAD"] = rfi

        print(get_rfi_names(rfi))

    return total_obs