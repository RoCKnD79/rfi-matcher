from typing import Self
import numpy as np
import pandas as pd
from datetime import datetime, timezone

class RaFilter:

    def __init__(self):
        # self.area = np.array([[-90, 90], [-180, 180]])  # [[lat_min, lat_max], [lon_min, lon_max]]
        self.lat_range = np.array([-90, 90])
        self.lon_range = np.array([-180, 180])
        self.freq_range = np.array([10, 1e6])  # MHz
        self.startTimeUTC = "2024-04-15T08:48:54.0"
        self.endTimeUTC = "2025-07-15T08:49:54.0"
        self.observatories = []

        self.filtered_df = None

        try:
            self.ra_csv_df = pd.read_csv("../../data/ITU_RA_Observatories.csv")

            # remove prefix spaces from column names
            self.ra_csv_df.columns = self.ra_csv_df.columns.str.strip()

            # remove prefix spaces from all text values in the file
            self.ra_csv_df = self.ra_csv_df.map(lambda x: x.strip() if isinstance(x, str) else x)
        except Exception as e: 
            return print("Error loading csv:", e)


    def set_observatories(self, names):
        """
        Set specific observatories of interest (if any)
        """
        if not isinstance(names, list):
            raise ValueError("Observatories must be provided as a list of strings.")
        
        # Ensure all elements are strings and strip whitespace
        cleaned_names = []
        for n in names:
            if not isinstance(n, str):
                raise ValueError("All observatory names must be strings.")
            cleaned_names.append(n.strip())
        
        self.observatories = cleaned_names
        return self


    def set_latitude(self, lat_range) -> Self:
        """
        Set the latitude range [min_lat, max_lat].
        """
        lat_range = np.array(lat_range, dtype=float)
        if lat_range.ndim != 1 or len(lat_range) != 2:
            raise ValueError("Latitude must be a 1D array of length 2: [min_lat, max_lat].")
        if not (-90 <= lat_range[0] <= 90 and -90 <= lat_range[1] <= 90):
            raise ValueError("Latitude values must be between -90 and 90.")
        if lat_range[0] > lat_range[1]:
            raise ValueError("Minimum latitude must be less than or equal to maximum latitude.")

        self.lat_range = lat_range
        return self

    def set_longitude(self, lon_range) -> Self:
        """
        Set the longitude range [min_lon, max_lon].
        """
        lon_range = np.array(lon_range, dtype=float)
        if lon_range.ndim != 1 or len(lon_range) != 2:
            raise ValueError("Longitude must be a 1D array of length 2: [min_lon, max_lon].")
        if not (-180 <= lon_range[0] <= 180 and -180 <= lon_range[1] <= 180):
            raise ValueError("Longitude values must be between -180 and 180.")
        if lon_range[0] > lon_range[1]:
            raise ValueError("Minimum longitude must be less than or equal to maximum longitude.")

        self.lon_range = lon_range
        return self

    def set_frequencies(self, freq_range) -> Self:
        """Set the frequency range in MHz."""
        freq_range = np.array(freq_range, dtype=float)
        if freq_range.ndim != 1 or len(freq_range) != 2:
            raise ValueError("Frequencies must be a 1D array of length 2: [min_freq, max_freq].")
        if np.any(freq_range <= 0):
            raise ValueError("Frequencies must be positive values (MHz).")
        if freq_range[0] > freq_range[1]:
            raise ValueError("Minimum frequency must be less than or equal to maximum frequency.")

        self.freq_range = freq_range
        return self

    def set_start_time(self, start_time) -> Self:
        """Set the start time in UTC (ISO 8601 format)."""
        self._validate_time_format(start_time)
        self.startTimeUTC = start_time

        return self

    def set_end_time(self, end_time) -> Self:
        """Set the end time in UTC (ISO 8601 format)."""
        self._validate_time_format(end_time)
        self.endTimeUTC = end_time

        return self

    def filter_observatories(self):

        df = self.ra_csv_df

        # check that 
        if self.observatories:
            print(self.observatories)
            #df[df["stn_name"].apply(lambda x: x == "PUBLIC")]
            self.filtered_df = df[df['stn_name'].isin(self.observatories)]
            return self.filtered_df

        #print(df)

        lat_min, lat_max = self.lat_range
        lon_min, lon_max = self.lon_range
        freq_min, freq_max = self.freq_range

        # Filter rows based on latitude and longitude
        location_filter = (
            (df['lat_dec'] >= lat_min) & 
            (df['lat_dec'] <= lat_max) & 
            (df['long_dec'] >= lon_min) & 
            (df['long_dec'] <= lon_max)
        )

        # Filter rows where the frequency range is entirely within [freq_min, freq_max]
        frequency_filter = (
            (df['freq_from'] >= freq_min) & 
            (df['freq_to'] <= freq_max)
        )

        # Combine filters
        self.filtered_df = df[location_filter & frequency_filter]

        return self.filtered_df



    def get_observatories(self):
        # extract the names of observatories meeting the filter parameters
        if self.filtered_df == None:
            self.filter_observatories()

        return self.filtered_df['stn_name'].dropna().drop_duplicates().tolist()


    def get_observatory_info(self, name):
        df = self.filtered_df
        return df[df['name'] == name]


    # ---------- INTERNAL VALIDATION ----------

    def _validate_time_format(self, time_str):
        """Helper function to ensure ISO 8601 UTC format."""
        try:
            datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            raise ValueError("Time must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sss")
