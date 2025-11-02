from model.filter_builder import RaFilter
from model.archive_dictionary import *


def main():
    ra_filter = (
        RaFilter()
            #.set_observatories(['VERY LARGE ARRAY NM', 'PARKES NSW', 'MEERKAT'])
            # .set_latitude([-40, 40])
            # .set_longitude([100, 110])
            .set_frequencies([241000, 275000])
    )

    observatories = ra_filter.get_observatories()
    print(observatories)

    # Iterate over filtered observatories
    for name in observatories:
        cls = ARCHIVE_CLASSES.get(name)
        if cls is None:
            print(f"Warning: No class defined for {name}")
            continue

        # Step 3: instantiate the object
        archive = cls()

        # Step 4: perform required operations
        # For example:
        # obj.download_data()
        # obj.process_data()
        archive.get_observations()
        print(f"Processing {archive.name} with {archive.__class__.__name__}")

        # Step 5: delete object to free memory
        del archive

    # nrao_archive = NraoDataArchive()

    # # Fetch all observations on NRAO portal up to a certain limit
    # observations = nrao_archive.get_observations()

    # # Filter out the observations that were done in the KA band
    # observations_ka = nrao_archive.get_target_observations(observations, {"KA"})

    # print("Observations:", observations_ka)

if __name__ == "__main__":
    main()