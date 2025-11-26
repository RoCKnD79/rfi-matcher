import requests
import os
from dotenv import load_dotenv

import pandas as pd

from astropy.time import Time
from astropy.coordinates import EarthLocation

from spacetrack import SpaceTrackClient
import spacetrack.operators as op

from model import utils
from .my_tle_fetcher_base import MyTleFetcherBase

load_dotenv()
IDENTITY = os.getenv("IDENTITY")
PASSWORD = os.getenv("PASSWORD")


class MyTleFetcherSpacetrack(MyTleFetcherBase):
    def _fetch_content(self):
        epoch = f'{self._begin}--{self._end}'

        with SpaceTrackClient(identity="user@example.com", password="password") as st:
            data = st.gp(
                iter_lines=True,
                epoch=epoch,
                format="tle",
            )
            
            return data