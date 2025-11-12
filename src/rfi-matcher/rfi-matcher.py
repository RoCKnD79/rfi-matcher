from model.filter_builder import RaFilter
from model.archive_dictionary import *
import katdal



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
    for name in observatories:
        cls = ARCHIVE_CLASSES.get(name)
        if cls is None:
            print(f"Warning: No class defined for {name}")
            continue

        # Instantiate the corresponding data archive object
        archive = cls(ra_filter)

        # Fetch the desired observations
        obs_data = archive.get_observations()
        print(f"Processing {archive.name} with {archive.__class__.__name__}")

        print(obs_data)

        # Delete the data archive object to free memory
        del archive


if __name__ == "__main__":
    main()