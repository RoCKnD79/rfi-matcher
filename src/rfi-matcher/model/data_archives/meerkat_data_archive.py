import pandas as pd
from datetime import datetime, timedelta
import asyncio

from astropy.coordinates import Angle
import astropy.units as u

from .. import utils
from . import meerkat_api

from .data_archive import DataArchive
from ..filter_builder import RaFilter

class MeerkatDataArchive(DataArchive):

    def __init__(self, ra_filter: RaFilter):
        self.name = "MeerKAT"
        self.ra_filter = ra_filter

    def get_observations(self, num=1):
        observations = self.get_raw_observations(num)

        observations = pd.DataFrame(observations)
        final_obs = self.format_to_sopp(observations)
        return final_obs
    

    def get_raw_observations(self, num=1) -> list[str]:
        flt = self.ra_filter

        # Get bands corresponding to frequencies of interest
        # Transform the list into the required string format for meerkat archive API
        bands = self.freq_to_bands(flt.freq_range[0], flt.freq_range[1])
        bands = ",".join(bands)

        # Get filter start/end time and extract date from it (i.e. 2025-10-03) --> requirement of meerkat archive API
        dt_start = datetime.fromisoformat(flt.startTimeUTC)
        start_date = dt_start.date()                    

        dt_end = datetime.fromisoformat(flt.endTimeUTC)
        end_date = dt_end.date()

        filters = [f"Band={bands}", f"from={start_date}", f"to={end_date}"]
        print(filters)


        # TODO understand why if fields="*" => product_type can't be None
        # something to do with fetched obkect being GraphQLObjectType instead of GraphQLScalarType
        # c.f. build_selection_block() of meerkat_api.py
        observations = asyncio.run(
            meerkat_api.data(
                auth_address="https://archive.sarao.ac.za",
                fields="rdb,MinFreq,MaxFreq,Bandwidth,Targets,DecRa,ProductReceivedTime,Duration",
                exclude_fields="products,FileSize",
                search="*",
                limit=num,
                show_fields=False,
                url_format=meerkat_api.URLFormat("external").value,
                filters=filters,
                no_check_certificate=False,
                sort=[],
                product_type=None,
            )
        )

        return observations


    def format_to_sopp(self, df):
        rows = []
        for _, row in df.iterrows():
            for decra_str in row["DecRa"]:
                dec, ra = map(lambda x: float(x.strip()), decra_str.split(","))  # split string and convert to float
                new_row = row.to_dict()
                new_row["declination"] = dec
                new_row["right_ascension"] = ra
                del new_row["DecRa"]
                rows.append(new_row)

        expanded_df = pd.DataFrame(rows)

        # Convert the declination column from degrees to dms string format
        expanded_df["declination"] = Angle(expanded_df["declination"].values * u.deg).to_string(unit=u.deg, sep='dms', precision=3)
        expanded_df["right_ascension"] = Angle(expanded_df["right_ascension"].values * u.deg).to_string(unit=u.hour, sep='hms', precision=1)

        # Rename "Bandwidth" to conform with format
        expanded_df = expanded_df.rename(columns={"Bandwidth": "bandwidth"})

        # convert MinFreq, MaxFreq columns into a center frequency property
        expanded_df['frequency'] = (expanded_df['MinFreq'] + expanded_df['MaxFreq']) / 2
        expanded_df = expanded_df.drop(columns=['MinFreq', 'MaxFreq'])

        expanded_df = expanded_df.drop(columns=['Targets', 'rdb'])

        # add name in first column
        expanded_df["name"] = [self.name]*len(expanded_df)

        # (1) Rename "ProductReceivedTime" → "begin"
        expanded_df = expanded_df.rename(columns={"ProductReceivedTime": "begin"})

        # (2) Convert begin to datetime (UTC) and compute "end"
        expanded_df["begin"] = pd.to_datetime(expanded_df["begin"], utc=True)
        expanded_df["end"] = expanded_df["begin"] + expanded_df["Duration"].apply(lambda s: timedelta(seconds=s))

        # (3) Convert both back to ISO strings (with 'Z' for UTC)
        expanded_df["begin"] = expanded_df["begin"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        expanded_df["end"] = expanded_df["end"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # (4) Drop Duration column (optional)
        expanded_df = expanded_df.drop(columns=["Duration"])

        return expanded_df[utils.get_sopp_order()]
