import pytest
import numpy as np
from model.filter_builder import ConfigurationBuilder  # Adjust filename if needed


# ---------- FIXTURE ----------

@pytest.fixture
def obj():
    """Provide a fresh instance of ConfigurationBuilder for each test."""
    return ConfigurationBuilder()


# ---------- TEST SET_LATITUDE ----------

def test_set_latitude_valid(obj):
    new_lat = [-45, 45]
    result = obj.set_latitude(new_lat)
    assert result is obj  # check chaining
    np.testing.assert_array_equal(obj.area[0], new_lat)

def test_set_latitude_invalid_shape(obj):
    with pytest.raises(ValueError, match="Latitude must be a 1D array of length 2"):
        obj.set_latitude([-45, 0, 45])

def test_set_latitude_invalid_range(obj):
    with pytest.raises(ValueError, match="Latitude values must be between -90 and 90"):
        obj.set_latitude([-120, 50])

def test_set_latitude_reversed(obj):
    with pytest.raises(ValueError, match="Minimum latitude must be less"):
        obj.set_latitude([10, -10])


# ---------- TEST SET_LONGITUDE ----------

def test_set_longitude_valid(obj):
    new_lon = [10, 100]
    result = obj.set_longitude(new_lon)
    assert result is obj
    np.testing.assert_array_equal(obj.area[1], new_lon)

def test_set_longitude_invalid_shape(obj):
    with pytest.raises(ValueError, match="Longitude must be a 1D array of length 2"):
        obj.set_longitude([0, 10, 20])

def test_set_longitude_invalid_range(obj):
    with pytest.raises(ValueError, match="Longitude values must be between -180 and 180"):
        obj.set_longitude([-200, 100])

def test_set_longitude_reversed(obj):
    with pytest.raises(ValueError, match="Minimum longitude must be less"):
        obj.set_longitude([50, -10])


# ---------- TEST SETTERS: FREQUENCIES ----------

def test_set_frequencies_valid(obj):
    new_freq = [50, 500]
    result = obj.set_frequencies(new_freq)
    assert result is obj
    np.testing.assert_array_equal(obj.frequencies, new_freq)

def test_set_frequencies_invalid_length(obj):
    with pytest.raises(ValueError, match="1D array of length 2"):
        obj.set_frequencies([10, 20, 30])

def test_set_frequencies_negative(obj):
    with pytest.raises(ValueError, match="must be positive"):
        obj.set_frequencies([-10, 100])

def test_set_frequencies_reversed(obj):
    with pytest.raises(ValueError, match="Minimum frequency must be less"):
        obj.set_frequencies([1000, 100])


# ---------- TEST SETTERS: TIME ----------

def test_set_start_time_valid(obj):
    new_time = "2025-10-13T09:00:00.0"
    result = obj.set_start_time(new_time)
    assert result is obj
    assert obj.startTimeUTC == new_time

def test_set_end_time_valid(obj):
    new_time = "2025-10-13T10:00:00.0"
    result = obj.set_end_time(new_time)
    assert result is obj
    assert obj.endTimeUTC == new_time

def test_set_start_time_invalid_format(obj):
    with pytest.raises(ValueError, match="Time must be in ISO 8601 format"):
        obj.set_start_time("2025/10/13 09:00:00")

def test_set_end_time_invalid_format(obj):
    with pytest.raises(ValueError, match="Time must be in ISO 8601 format"):
        obj.set_end_time("13-10-2025T09:00:00")


# ---------- TEST DEFAULT VALUES ----------

def test_default_area(obj):
    np.testing.assert_array_equal(obj.area, np.array([[-90, 90], [-180, 180]]))

def test_default_frequencies(obj):
    np.testing.assert_array_equal(obj.frequencies, np.array([10, 3000]))

def test_default_start_time(obj):
    assert obj.startTimeUTC == "2025-10-13T08:48:54.0"

def test_default_end_time(obj):
    assert obj.endTimeUTC == "2025-10-13T08:49:54.0"