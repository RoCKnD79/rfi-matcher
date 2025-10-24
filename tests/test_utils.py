import pytest
from utils import *

import skrf as rf


# ========= polar_to_complex() =========

def test_polar_to_complex_exception_on_different_amplitude_and_phases_lengths():
    with pytest.raises(AssertionError):
        polar_to_complex(np.zeros(1), np.zeros(2))


def test_complete_ft_evenN():
    magnitudes = np.array([3,2,1,0])
    phases = np.zeros(len(magnitudes))
    X_f = complete_ft(magnitudes, phases)

    # test if conjugate symmetric
    F_flipped = np.concatenate((X_f[:1], np.flip(X_f[1:])))
    assert np.all(np.isclose(X_f, np.conj(F_flipped)))


# ========= generate_Ascan() =========

def test_generate_Ascan_with_emptyOrNone():
    with pytest.raises(IndexError):
        generate_Ascan(np.array([]), np.array([]))

    with pytest.raises(TypeError):
        generate_Ascan(None, None)

    
def test_delta_tf_raises_error_with_emptyOrNone_vector():
    empty_or_none(delta_tf)


#========= helper functions =========

def empty_or_none(func):
    with pytest.raises(IndexError):
        func(np.array([]))

    with pytest.raises(TypeError):
        func(None)