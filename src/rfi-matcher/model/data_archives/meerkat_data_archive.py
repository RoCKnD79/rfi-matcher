import pandas as pd
from datetime import datetime
import asyncio

from . import meerkat_api

from .data_archive import DataArchive
from ..filter_builder import RaFilter

class MeerkatDataArchive(DataArchive):

    def __init__(self, ra_filter: RaFilter):
        self.name = "MeerKAT"
        self.ra_filter = ra_filter

    def get_observations(self):
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
        asyncio.run(
            meerkat_api.data(
                auth_address="https://archive.sarao.ac.za",
                fields="*",
                exclude_fields="products,FileSize",
                search="*",
                limit=1,
                show_fields=False,
                url_format=meerkat_api.URLFormat("external").value,
                filters=filters,
                no_check_certificate=False,
                sort=[],
                product_type=None,
            )
        )
