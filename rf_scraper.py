from urllib.request import urlopen
import json
import pandas as pd

# url = "https://data.nrao.edu/archive-service/restapi_product_details_view?sdm_id=25B-104.sb49474829.eb49602275.60965.561376909725"

START = 0
NUM_ROWS = 25

NRAO_PORTAL_URL = f"https://data.nrao.edu/archive-service/restapi_get_eb_project_view?start={START}&rows={NUM_ROWS}&sort=proj_stop%20desc"


def get_html(url):
    '''
    Returns json data read from the url given in parameter    
    '''
    page = urlopen(url)

    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    return json.loads(html)


def main():
    # Read list of projects from NRAO data archive portal
    # nrao_portal_data = get_html(NRAO_PORTAL_URL)
    nrao_portal_data = get_html("https://archive.sarao.ac.za/graphql")
    #print(json.dumps(parsed, indent=2))

    # Extract list of project IDs
    projects = nrao_portal_data["project_dict"]["projects"]
    print(json.dumps(nrao_portal_data, indent=2))
    # project_codes = [project["project_code"] for project in projects if "project_code" in project]

    # print('\n'*20)

    # for code in project_codes[:2]:
    #     project_url = f"https://data.nrao.edu/archive-service/restapi_get_paged_exec_blocks?start=0&rows=25&sort=obs_stop%20desc&project_code=%22{code}%22"
    #     project_data = get_html(project_url)

    #     print(json.dumps(project_data, indent=2), '\n\n')

    # print(project_codes)


if __name__ == "__main__":
    main()
# print(html)