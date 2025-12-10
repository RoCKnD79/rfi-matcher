import pandas as pd

from .data_archive import DataArchive
from ..rfi_filter import RaFilter

class NraoDataArchive(DataArchive):
    name = "NRAO"
    latitude = 34.083
    longitude = -107.617
    elevation =	2124

    def __init__(self, ra_filter: RaFilter):
        super().__init__(ra_filter)

        START = 0
        NUM_ROWS = 5

        self.start = START
        self.num_rows = NUM_ROWS


    def get_observations(self):
        # NRAO_PORTAL_URL = f"https://data.nrao.edu/archive-service/restapi_get_eb_project_view?start={START}&rows={NUM_ROWS}&sort=proj_stop%20desc"

        # Read list of projects from NRAO data archive portal
        project_codes = self.get_project_codes()

        df = pd.DataFrame()
        for code in project_codes:
            project_url = self.get_url_project(code)
            print('url:', project_url)
            project_data = self.get_html(project_url)

            observations = [
                {"obs_id": p["obs_id"],
                "obs_band": p["obs_band"]}
                for p in project_data["eb_list"]
                if "obs_id" in p and "project_code" in p and "obs_band" in p
            ]
            
            df = pd.concat([df, pd.DataFrame(observations)], ignore_index=True, sort=False)

        return df
            

    def get_target_observations(self, observations: pd.DataFrame, target_bands = {"KA"}) -> pd.DataFrame:
        # target_bands = {"KA", "Q"}  # use a set for faster lookup
        interest_obs = observations[observations["obs_band"].apply(lambda x: any(b in target_bands for b in x))]

        return interest_obs


    def get_project_codes(self):
        NRAO_PORTAL_URL = f"https://data.nrao.edu/archive-service/restapi_get_eb_project_view?start={self.start}&rows={self.num_rows}&sort=proj_stop%20desc"
        nrao_portal_data = self.get_html(NRAO_PORTAL_URL)

        # Extract list of project IDs
        projects = nrao_portal_data["project_dict"]["projects"]
        pd_projects = pd.DataFrame(projects)
        # print(projects)

        project_codes = [project["project_code"] for project in projects if "project_code" in project]
        # print(project_codes)
        return project_codes


    def get_url_project(self, project_code):
        return f"https://data.nrao.edu/archive-service/restapi_get_paged_exec_blocks?start={self.start}&rows={self.num_rows}&sort=obs_stop%20desc&project_code=%22{project_code}%22"


    def get_url_observation(self, observation_id):
        return f"https://data.nrao.edu/archive-service/restapi_product_details_view?sdm_id={observation_id}"
        