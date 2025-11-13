from model.filter_builder import RaFilter
from model.archive_dictionary import *
import katdal

from model.utils import get_rfi_sources
import pandas as pd

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
        print(obs_df)
        print(f"Processing {archive.name} with {archive.__class__.__name__}")

        observations.append(obs_df)

        # Delete the data archive object to free memory
        del archive

    full_df = pd.concat(observations, ignore_index=True)
    print(full_df)

    rfi_satellites = []
    for _, obs in full_df.iterrows():
        rfi_satellites.append(get_rfi_sources(obs))

    print(rfi_satellites)


if __name__ == "__main__":
    main()