# import requests

# url = 'https://archive.sarao.ac.za/graphql'
# query = """
# query ($search: String, $filters: [ProductFilterInput!], $cursor: String, $limit: Int, $sort: [SortColumnInput!]) {
#   captureBlocks(
#     search: $search
#     filters: $filters
#     cursor: $cursor
#     limit: $limit
#     sort: $sort
#   ) {
#     pageInfo {
#       startCursor
#       endCursor
#       hasNextPage
#       hasPreviousPage
#       totalCount
#     }
#     records {
#       id
#       CaptureBlockId
#       ProposalId
#       MinFreq
#       Duration
#       MaxFreq
#       Bandwidth
#       Antennas
#       Targets
#       Description
#       ChannelWidth
#       StartTime
#       NumFreqChannels
#       productExpirySummary
#       Observer
#       ScheduleBlockIdCode
#       missingItems {
#         id
#         filesMissing
#       }
#       QA2
#       Public
#       sizeInBytes
#       transferSummary
#       proposal {
#         id
#         TransferFacility
#       }
#       exports {
#         records {
#           id
#         }
#       }
#     }
#   }
# }
# """

# variables = {
#   "search": "",
#   "filters": [],
#   "limit": 10,
#   "cursor": "",
#   "sort": []
# }

# payload = {
#     "query": query,
#     "variables": variables
# }

# # For the Cookie part. The format is the following: "sessionid=[cookie value read in DevTools]; csrftoken=[value read in X-CSRF token in DevTools]"
# # In DevTools in the "Network" tab, select "Preserve Log" and "Fetch/XHR". Reload page. Look in the "Headers tab below".
# # For the variables and query data I wrote above. It is found in the "Payload" tab (the one next to "Headers")
# headers = {
#     "Content-Type": "application/json",
#     "Cookie": "sessionid=_ga=GA1.3.1267883327.1759688908; _ga_MJPM7NJY41=GS2.1.s1759688908$o1$g1$t1759688946$j22$l0$h0; client-id=16994a5f-b69f-4e14-ac3f-a311d9f16ff2; auth=gAAAAABo9VeVWu0nIMCMGdHQcx6Kd6qFzoM5blXU0DiS9G4LyZVbYvLTgT0Bb5lGbXDRUfT05iLDfuaFc-PvR3s5PW2l8KoQap9HkV1T6YtgGzeptyjICjXUqpm4Ohb9blN2yJtxJyLOi6HLnY_OD153gnD0B_suo5kuojJhL3MshNQfhw94koSvIzcMqu1Mgnrz3rJY-ly9; csrftoken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjc3JmIjoiY3NyZl90b2tlbiIsImV4cCI6MTc2MDk5Mzk5NX0.ZJy6uCeNbdvJYfvl0mdghaFlJS_hKnwsBUQ-ur36hVw;"
# }

# response = requests.post(url, json=payload, headers=headers)
# print(response.json())


# __main__.py
"""
pip install "gql[requests]" requests
"""
from login import login, build_config, load_token
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from datetime import datetime, timedelta, timezone

# Build login configuration object
config = build_config("https://archive.sarao.ac.za")

# Force login
login(config)

# Create HTTP client
client = Client(
    transport=RequestsHTTPTransport(
        url=f"{config.get('base_url')}/graphql",
        headers={"Authorization": f"Bearer {load_token(config.get('token_path'))}"},
        verify=True,
    ),
    fetch_schema_from_transport=False,
)

# Define GraphQL query
query = gql(
    """
    query ($limit: Int, $cursor: String, $search: String, $filters: [ProductFilterInput!]) {
      captureBlocks(limit: $limit, cursor: $cursor, search: $search, filters: $filters) {
        pageInfo {
          totalCount
          endCursor
          hasNextPage
        }
        records {
          id
          CaptureBlockId
          Description
          QA2
          rdb
        }
      }
    }
    """
)

N = 360
date_N_days_ago = (
    (datetime.now(timezone.utc) - timedelta(days=N))
    .isoformat(timespec="milliseconds")
    .replace("+00:00", "Z")
)


limit = 20
cursor = None
search = "*"
filters = [
    {"field": "TransferStatus", "value": "AVAILABLE"},
    {
        "field": "dateRange",
        "value": [
            date_N_days_ago,
            None,
        ],
    },
]


try:
    while True:
        variables = {
            "limit": limit,
            "cursor": cursor,
            "search": search,
            "filters": filters,
        }
        result = client.execute(query, variable_values=variables)
        records = result["captureBlocks"]["records"]
        page_info = result["captureBlocks"]["pageInfo"]

        for record in records:
            print(record)

        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

except TransportQueryError as e:
    errors = e.errors or []
    print(errors)
    raise

except Exception as e:
    raise