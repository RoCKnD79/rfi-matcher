import numpy as np
from skyfield.api import load

from . import time_utils
from sopp.custom_dataclasses.satellite.satellite import Satellite


def linspace_sky_times(start_iso: str, end_iso: str, npoints=10):
    """
    Convert ISO start/end time into n Skyfield Time objects,
    evenly spaced between the interval.
    """
    ts = load.timescale()

    dt_start = time_utils.iso_to_datetime(start_iso)
    dt_end   = time_utils.iso_to_datetime(end_iso)

    # Generate list of evenly spaced datetimes
    times = [dt_start + i * (dt_end - dt_start) / (npoints - 1) for i in range(npoints)]
    sky_times = ts.from_datetimes(times)

    return sky_times
 

def ra_str_to_deg(ra_str):
    """
    Convert RA string in format '[-]HhMmSs' to decimal degrees.
    Example: '-4h20m35.0s' -> -65.1458333 degrees
    """
    ra_str = ra_str.strip()
    sign = -1 if ra_str.startswith('-') else 1
    ra_str = ra_str.lstrip('+-')

    # Split components
    h_part, rest = ra_str.split('h')
    m_part, s_part = rest.split('m')
    s_part = s_part.rstrip('s')

    hours = float(h_part)
    minutes = float(m_part)
    seconds = float(s_part)

    # Convert to degrees: 1h = 15 deg
    degrees = 15 * (hours + minutes/60 + seconds/3600)

    return sign * degrees


def dec_str_to_deg(dec_str):
    """
    Convert Dec string in format '[-]DdMmSs' to decimal degrees.
    Example: '-63d42m45.601s' -> -63.712667 degrees
    """
    dec_str = dec_str.strip()
    sign = -1 if dec_str.startswith('-') else 1
    dec_str = dec_str.lstrip('+-')

    # Split components
    d_part, rest = dec_str.split('d')
    m_part, s_part = rest.split('m')
    s_part = s_part.rstrip('s')

    degrees = float(d_part)
    minutes = float(m_part)
    seconds = float(s_part)

    dec_deg = degrees + minutes/60 + seconds/3600
    return sign * dec_deg



def radec_to_vector(ra_deg, dec_deg):
    """Convert RA/Dec in degrees to 3D unit vector."""
    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)
    x = np.cos(dec_rad) * np.cos(ra_rad)
    y = np.cos(dec_rad) * np.sin(ra_rad)
    z = np.sin(dec_rad)
    return np.array([x, y, z]).T  # shape (N,3) if ra/dec are arrays



def closest_radec(ra_array, dec_array, target_ra_deg, target_dec_deg):
        """
        Find the RA/Dec in the arrays closest to the target point.
        
        Parameters:
            ra_array, dec_array: arrays of RA/Dec in degrees
            target_ra_deg, target_dec_deg: target RA/Dec in degrees
        Returns:
            idx: index of closest point
            closest_ra, closest_dec: RA/Dec of closest point
            angular_distance_deg: angular distance in degrees
        """
        sat_vec = radec_to_vector(ra_array, dec_array)
        target_vec = radec_to_vector(target_ra_deg, target_dec_deg).reshape(1,3)

        # Cosine of angular separation
        cos_theta = np.sum(sat_vec * target_vec, axis=1)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)  # numerical safety
        angular_distance_deg = np.degrees(np.arccos(cos_theta))

        # Index of closest approach
        idx = np.argmin(angular_distance_deg)
        return idx, ra_array[idx], dec_array[idx], angular_distance_deg[idx]



def sat_proximity(sat: Satellite, obs_start, obs_end, target_ra, target_dec, npoints=1000):

        eo = sat.to_rhodesmill()

        sat_timestamps = linspace_sky_times(obs_start, obs_end, npoints)
        geocentric = eo.at(sat_timestamps)
        right_ascensions, declinations, _ = geocentric.radec()

        # print("\nSAT RAs:", right_ascensions.degrees)
        # print("SAT DECs:", declinations.degrees)

        idx, ra, dec, ang_dist = closest_radec(right_ascensions.degrees, declinations.degrees, target_ra, target_dec)
        timestamp = sat_timestamps[idx].utc_datetime()

        return timestamp, ra, dec, ang_dist