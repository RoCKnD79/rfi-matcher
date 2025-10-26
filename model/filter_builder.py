from typing import Self
import numpy as np
from datetime import datetime, timezone

class ConfigurationBuilder:

    def __init__(self):
        self.area = np.array([[-90, 90], [-180, 180]])  # [[lat_min, lat_max], [lon_min, lon_max]]
        self.frequencies = np.array([10, 3000])  # MHz
        self.startTimeUTC = "2025-10-13T08:48:54.0"
        self.endTimeUTC = "2025-10-13T08:49:54.0"


    def set_latitude(self, latitude) -> Self:
        """
        Set the latitude range [min_lat, max_lat].
        """
        latitude = np.array(latitude, dtype=float)
        if latitude.ndim != 1 or len(latitude) != 2:
            raise ValueError("Latitude must be a 1D array of length 2: [min_lat, max_lat].")
        if not (-90 <= latitude[0] <= 90 and -90 <= latitude[1] <= 90):
            raise ValueError("Latitude values must be between -90 and 90.")
        if latitude[0] > latitude[1]:
            raise ValueError("Minimum latitude must be less than or equal to maximum latitude.")

        self.area[0] = latitude
        return self

    def set_longitude(self, longitude) -> Self:
        """
        Set the longitude range [min_lon, max_lon].
        """
        longitude = np.array(longitude, dtype=float)
        if longitude.ndim != 1 or len(longitude) != 2:
            raise ValueError("Longitude must be a 1D array of length 2: [min_lon, max_lon].")
        if not (-180 <= longitude[0] <= 180 and -180 <= longitude[1] <= 180):
            raise ValueError("Longitude values must be between -180 and 180.")
        if longitude[0] > longitude[1]:
            raise ValueError("Minimum longitude must be less than or equal to maximum longitude.")

        self.area[1] = longitude
        return self

    def set_frequencies(self, frequencies) -> Self:
        """Set the frequency range in MHz."""
        frequencies = np.array(frequencies, dtype=float)
        if frequencies.ndim != 1 or len(frequencies) != 2:
            raise ValueError("Frequencies must be a 1D array of length 2: [min_freq, max_freq].")
        if np.any(frequencies <= 0):
            raise ValueError("Frequencies must be positive values (MHz).")
        if frequencies[0] > frequencies[1]:
            raise ValueError("Minimum frequency must be less than or equal to maximum frequency.")

        self.frequencies = frequencies
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


    # ---------- INTERNAL VALIDATION ----------

    def _validate_time_format(self, time_str):
        """Helper function to ensure ISO 8601 UTC format."""
        try:
            datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            raise ValueError("Time must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sss")
