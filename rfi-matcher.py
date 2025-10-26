from model.filter_builder import ConfigurationBuilder
from model.data_archives.nrao_data_archive import NraoDataArchive


def main():
    builder = (
        ConfigurationBuilder()
            .set_latitude([-10, 40])
            .set_longitude([100, 110])
            .set_frequencies([1000, 10000])
    )

    nrao_archive = NraoDataArchive()

    observations = nrao_archive.get_observations()
    observations_ka = nrao_archive.get_target_observations(observations, {"KA"})

    print("Observations:", observations_ka)

if __name__ == "__main__":
    main()