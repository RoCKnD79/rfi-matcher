import pandas as pd
from pathlib import Path

from sopp.sopp import Sopp
from sopp.builder.configuration_builder import ConfigurationBuilder
from sopp.tle_fetcher.tle_fetcher_celestrak import TleFetcherCelestrak

def get_rfi_sources(df_obs: pd.DataFrame):

    name = "MEERKAT"

    configuration = (
        ConfigurationBuilder()
        .set_facility(
            latitude=-30.7128,
            longitude=21.4436,
            elevation=1086.6,
            name=name,
            beamwidth=3,
        )
        .set_frequency_range(
            bandwidth=df_obs['bandwidth'],
            frequency=df_obs['frequency']
        )
        .set_time_window(
            begin='2025-11-13T08:48:54.0',#df_obs['begin'],
            end='2025-11-13T08:49:54.0' #df_obs['end']
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
    rfi_overhead = sopp_obj.get_satellites_crossing_main_beam()

    rfi_satellites = []
    for sat in rfi_overhead:
        rfi_satellites.append(sat.satellite.name)

    return rfi_satellites



def get_sopp_order():
    return ["name", "frequency", "bandwidth", "declination", "right_ascension", "begin", "end", "url"]