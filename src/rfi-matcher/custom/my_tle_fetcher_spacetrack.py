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
        # epoch = f'{self._begin}--{self._end}'

        # try:
        #     with SpaceTrackClient(identity=IDENTITY, password=PASSWORD) as st:
        #         data = st.gp(
        #             epoch=epoch,
        #             format="tle",
        #         )

        #         response = requests.models.Response()
        #         response.status_code = 200
        #         response._content = data.encode('utf8')

        #         print(data)

        #         return response
            
        # except Exception as e:
        #     print(f"Error fetching TLE data: {str(e)}")
        #     raise

        session = requests.Session()

        login_url = "https://www.space-track.org/ajaxauth/login"
        payload = {
            "identity": IDENTITY,
            "password": PASSWORD,
        }

        # Send login request
        resp = session.post(login_url, data=payload)
        print("Login status:", resp.status_code)
        print("Login resp headers:", resp.headers)

        # Try parse JSON body, but guard for 204
        if resp.status_code == 200:
            try:
                data = resp.json()
                print("Login JSON:", data)
            except ValueError:
                print("No JSON in response")
        elif resp.status_code == 204:
            print("204 returned: likely login success, no JSON body")
        else:
            print("Login returned unexpected status:", resp.status_code, resp.text)
            resp.raise_for_status()

        # Now make an API request using the same session
        # query = "https://www.space-track.org/basicspacedata/query/class/gp/decay_date/null-val/epoch/>now-30/orderby/norad_cat_id/format/3le"
        query = f"https://www.space-track.org/basicspacedata/query/class/gp/epoch/{self._begin}--{self._end}/orderby/norad_cat_id/format/3le"
        resp2 = session.get(query)
        return resp2