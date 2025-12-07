import requests
import os
from dotenv import load_dotenv

from spacetrack import SpaceTrackClient
import spacetrack.operators as op

from .my_tle_fetcher_base import MyTleFetcherBase

load_dotenv()
IDENTITY = os.getenv("IDENTITY")
PASSWORD = os.getenv("PASSWORD")


class MyTleFetcherSpacetrack(MyTleFetcherBase):
    def _fetch_content(self):
        epoch = f'{self._begin}--{self._end}'

        try:
            with SpaceTrackClient(identity=IDENTITY, password=PASSWORD) as st:
                data = st.gp(
                    epoch=epoch,
                    format="3le",
                    object_type="Payload"
                )

                response = requests.models.Response()
                response.status_code = 200
                response._content = data.encode('utf8')

                print(data)

                return response
            
        except Exception as e:
            print(f"Error fetching TLE data: {str(e)}")
            raise