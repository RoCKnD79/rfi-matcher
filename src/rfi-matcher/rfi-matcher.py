import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import katdal
from skyfield.api import EarthSatellite
from skyfield.timelib import Time

from sopp.custom_dataclasses.satellite.satellite import Satellite
from sopp.tle_fetcher.tle_fetcher_celestrak import TleFetcherCelestrak
from sopp.tle_fetcher.tle_fetcher_spacetrack import TleFetcherSpacetrack

from model.filter_builder import RaFilter
from model.archive_dictionary import *
from model.sopp_iface import get_rfi_sources
from model import utils

def main(fetch_tles=True, satellites_filepath=Path('')):

    if fetch_tles:
        if not satellites_filepath.exists():
            print("Fetching satellite TLEs:", satellites_filepath)
            TleFetcherCelestrak(satellites_filepath).fetch_tles()
            # TleFetcherSpacetrack(satellites_filepath).fetch_tles()

    ra_filter = (
        RaFilter()
            .set_observatories(['MEERKAT'])
            # .set_frequencies([500, 1100])
            # .set_observatories(['VERY LARGE ARRAY NM', 'PARKES NSW', 'MEERKAT'])
            # .set_latitude([-40, 40])
            # .set_longitude([100, 110])
            # .set_frequencies([241000, 275000])
            # .set_start_time("2025-04-15T08:49:54.0")
            # .set_end_time("2025-07-02T10:32:48.0")
    )

    observatories = ra_filter.get_observatories()
    print(observatories)

    # Iterate over filtered observatories
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
        obs_df = archive.get_observations()
        observations.append(obs_df)

        # Delete the data archive object to free memory
        del archive

    total_obs = pd.concat(observations, ignore_index=True)
    print(total_obs)

    total_obs["NORAD"] = None

    for i, obs in total_obs.iterrows():
        if(i > 0): break
        print('\nprocessing row', i)
        rfi = get_rfi_sources(obs)
        total_obs.at[i, "NORAD"] = rfi

    eo = rfi[0].to_rhodesmill()
    
    sat_timestamps = utils.linspace_sky_times('2025-11-13T08:48:54.0', '2025-11-13T08:49:54.0')
    geocentric = eo.at(sat_timestamps)
    km = geocentric.position.km
    right_ascensions, declinations, distances = geocentric.radec()

    print("\nSAT RAs:", right_ascensions.degrees)
    print("SAT DECs:", declinations.degrees)

    target_ra = utils.ra_str_to_deg('-4h20m35.0s')
    target_dec = utils.dec_str_to_deg('-63d42m45.601s')

    print('\nTarget RA:', target_ra)
    print('Target DEC:', target_dec)

    idx, ra, dec, ang_dist = utils.closest_radec(right_ascensions.degrees, declinations.degrees, target_ra, target_dec)
    print('\nidx:', idx)
    print('ra:', ra)
    print('dec:', dec)
    print('ang_dist:', ang_dist)

    # name = "CALSPHERE 1"     
    # line1 = "1 00900U 64063C   25318.27805289  .00001492  00000+0  15168-2 0  9996"
    # line2 = "2 00900  90.2209  66.7944 0025285 219.0423 169.4006 13.76311253 41869"

    # eo = EarthSatellite(line1, line2, name)

    # ts = eo.epoch
    # dt = ts.utc_datetime()

    # sat_timestamps = utils.linspace_sky_times("2025-11-14T08:49:54.0", "2025-11-14T08:59:54.0")
    # print(sat_timestamps)

    # geocentric = eo.at(sat_timestamps)
    # km = geocentric.position.km
    # right_ascensions, declinations, distances = geocentric.radec()
    
    # for ra in right_ascensions.hours:
    #     print(ra)

    # for dec in declinations.degrees:
    #     print(dec)


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
        satellites_filepath.unlink(missing_ok=True)

    # main()
        