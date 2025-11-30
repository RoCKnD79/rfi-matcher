import re
import pandas as pd
from datetime import datetime, timedelta
import asyncio

from astropy.coordinates import Angle
import astropy.units as u

from . import meerkat_api

from .data_archive import DataArchive
from ..rfi_filter import RaFilter

class MeerkatDataArchive(DataArchive):

    name = "MEERKAT"
    latitude = -30.7128
    longitude = 21.4436
    elevation = 0

    def __init__(self, ra_filter: RaFilter):
        self.ra_filter = ra_filter
        

    def get_observations(self, num=1):
        '''
        Return 'num' number of MeerKAT observations
        based on self.ra_filter's filtering parameters
        '''
        observations = self.get_raw_observations(num)
        final_obs = self.__format_to_sopp(observations)
        return final_obs
    

    def get_raw_observations(self, num=1, fields="rdb,ProductId,MinFreq,MaxFreq,Bandwidth,Targets,DecRa,StartTime,Duration,details") -> pd.DataFrame:
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
        print('\n\nfilters:', filters, '\n\n')


        # TODO understand why if fields="*" => product_type can't be None
        # something to do with fetched object being GraphQLObjectType instead of GraphQLScalarType
        # c.f. build_selection_block() of meerkat_api.py
        observations = asyncio.run(
            meerkat_api.data(
                auth_address="https://archive.sarao.ac.za",
                fields=fields,
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

        return pd.DataFrame(observations)


    def __format_to_sopp(self, df):

        rows = []
        # iterate on observations
        for _, row in df.iterrows():
            # break down each observation session into its respective track observations
            tracks = self.__extract_tracks(row)
            for t in tracks:
                new_row = row.to_dict()
                new_row["declination"] = t["declination"]
                new_row["right_ascension"] = t["right_ascension"]
                new_row["begin"] = t["begin"]
                new_row["end"] = t["end"]
                rows.append(new_row)

        expanded_df = pd.DataFrame(rows)

        # Convert the declination column from degrees to dms string format
        expanded_df["declination"] = Angle(expanded_df["declination"].values * u.deg).to_string(unit=u.deg, sep='dms', precision=3)
        
        # MeerKAT archive may return negative RAs => convert to positive degrees (between 0 and 360)
        right_ascensions = (expanded_df["right_ascension"].values + 360) % 360
        expanded_df["right_ascension"] = Angle(right_ascensions * u.deg).to_string(unit=u.hour, sep='hms', precision=1)

        # Rename "Bandwidth" and "rdb" to conform with sopp config format
        expanded_df = expanded_df.rename(columns={"Bandwidth": "bandwidth", "rdb": "url", "ProductId": "observation_id"})

        # convert MinFreq, MaxFreq columns into a center frequency property
        expanded_df['frequency'] = (expanded_df['MinFreq'] + expanded_df['MaxFreq']) / 2

        # add name in first column
        expanded_df["name"] = [self.name]*len(expanded_df)

        # Drop unused columns
        expanded_df = expanded_df.drop(columns=['MinFreq', 'MaxFreq'])
        expanded_df = expanded_df.drop(columns=['Targets'])
        expanded_df = expanded_df.drop(columns=["Duration"])

        return expanded_df[self.get_df_order()]
    

    def __extract_tracks(self, df_row):
        """
        Extract tracking scan information from a Meerkat observation metadata row.

        This method parses the structured text contained in the ``details`` column of
        a dataframe row to extract all scans whose ScanState is ``track``. For each
        tracking scan, it extracts:

        - the track index (CompScanLabel),
        - the target identifier (e.g., ``"J0437-4715"``),
        - its declination and right ascension,
        - the start and end timestamps of the scan.

        Start and end times are converted to full ISO-8601 timestamps using the date
        contained in the ``StartTime`` column of the dataframe row.

        Target celestial coordinates (Dec/Ra) are obtained from the dictionary 
        provided by ``self.__target_decra_dict(df_row)``, which maps each target name 
        to a string of the form ``"dec, ra"``.

        Parameters
        ----------
        df_row : pandas.Series
            A row from the observations dataframe containing at minimum:
            - ``details`` : str  
                The raw multi-line metadata text retrieved from the Meerkat archive.
            - ``StartTime`` : datetime-like  
                Used to determine the observation date.
            Additional fields used by ``__target_decra_dict`` may also be required.

        Returns
        -------
        list of dict
            A list of dictionaries, one per tracking scan.  
            Each dictionary has the structure::

                {
                    "track": <int>,              # track index (CompScanLabel)
                    "target_id": <str>,          # target identifier (e.g. "J0437-4715")
                    "declination": <float>,      # target declination (deg)
                    "right_ascension": <float>,  # target right ascension (deg)
                    "begin": <str>,              # ISO timestamp for scan start
                    "end": <str>,                # ISO timestamp for scan end
                }

            If no tracking scans are present, an empty list is returned.

        Notes
        -----
        - Only scans with ScanState ``track`` are included.
        - The final ``<index>:<targetID>`` field on each scan line is used to extract 
        the correct target identifier, avoiding interference from earlier ``:track`` 
        tokens in the same line.
        """

        pattern = re.compile(
            r"(?P<start>\d{2}:\d{2}:\d{2})\s*-\s*(?P<end>\d{2}:\d{2}:\d{2})"
            r".*?(?P<track>\d+):track"                 # first track: label
            r".*?(?P<target_index>\d+):(?P<target_id>[A-Za-z0-9\-]+)\s*$",  # final target at end of line
            flags=re.MULTILINE
        )

        text = df_row["details"]
        date_obj = pd.to_datetime(df_row["StartTime"]).date()
        target_decra = self.__target_decra_dict(df_row)

        results = []

        for m in pattern.finditer(text):

            start_t = m.group("start")
            end_t   = m.group("end")
            track   = int(m.group("track"))
            target_id = m.group("target_id")

            # Convert to full ISO timestamps
            start_iso = datetime.combine(date_obj, datetime.strptime(start_t, "%H:%M:%S").time()).isoformat()
            end_iso   = datetime.combine(date_obj, datetime.strptime(end_t, "%H:%M:%S").time()).isoformat()

            # Get dec/ra strings from mapping → split
            try: 
                dec_str, ra_str = target_decra[target_id].split(",")
                dec = float(dec_str)
                ra = float(ra_str)

                results.append({
                    "track": track,
                    "target_id": target_id,
                    "declination": dec,
                    "right_ascension": ra,
                    "begin": start_iso,
                    "end": end_iso,
                })

            except Exception as e:
                print("Error:", str(e))
                continue

        return results



    def __target_decra_dict(self, df_row):
        targets = df_row["Targets"] 
        decra = df_row["DecRa"]  

        target_map = dict(zip(targets, decra))
        return target_map