import pandas as pd
from pathlib import Path

from sopp.sopp import Sopp
from sopp.custom_dataclasses.satellite.satellite import Satellite
from sopp.builder.configuration_builder import ConfigurationBuilder
from sopp.tle_fetcher.tle_fetcher_celestrak import TleFetcherCelestrak

from rfi_matcher.model.archive_dictionary import *

def get_rfi_sources(df_obs: pd.DataFrame, 
                    tle_file_path = 'data/satellites.tle', 
                    frequency_file_path = 'data/satellite_frequencies.csv', 
                    beamwidth = 3,
                    mainbeam=True
                    ) -> list[Satellite]:
    '''
    mainbeam = True (satellites crossing mainbeam)
    mainbeam = False (all satellites above horizon)
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
            beamwidth=beamwidth,
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
        .set_satellites(tle_file=tle_file_path, frequency_file=frequency_file_path)
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