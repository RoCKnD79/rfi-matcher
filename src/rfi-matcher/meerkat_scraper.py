import requests

url = 'https://archive.sarao.ac.za/graphql'
query = """
query ($search: String, $filters: [ProductFilterInput!], $cursor: String, $limit: Int, $sort: [SortColumnInput!]) {
  captureBlocks(
    search: $search
    filters: $filters
    cursor: $cursor
    limit: $limit
    sort: $sort
  ) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
      totalCount
    }
    records {
      id
      CaptureBlockId
      ProposalId
      MinFreq
      Duration
      MaxFreq
      Bandwidth
      Antennas
      Targets
      Description
      ChannelWidth
      StartTime
      NumFreqChannels
      productExpirySummary
      Observer
      ScheduleBlockIdCode
      missingItems {
        id
        filesMissing
      }
      QA2
      Public
      sizeInBytes
      transferSummary
      proposal {
        id
        TransferFacility
      }
      exports {
        records {
          id
        }
      }
    }
  }
}
"""

variables = {
  "search": "",
  "filters": [],
  "limit": 10,
  "cursor": "",
  "sort": []
}

payload = {
    "query": query,
    "variables": variables
}

# For the Cookie part. The format is the following: "sessionid=[cookie value read in DevTools]; csrftoken=[value read in X-CSRF token in DevTools]"
# In DevTools in the "Network" tab, select "Preserve Log" and "Fetch/XHR". Reload page. Look in the "Headers tab below".
# For the variables and query data I wrote above. It is found in the "Payload" tab (the one next to "Headers")
headers = {
    "Content-Type": "application/json",
    "Cookie": "sessionid=_ga=GA1.3.1267883327.1759688908; _ga_MJPM7NJY41=GS2.1.s1759688908$o1$g1$t1759688946$j22$l0$h0; client-id=16994a5f-b69f-4e14-ac3f-a311d9f16ff2; auth=gAAAAABo9VeVWu0nIMCMGdHQcx6Kd6qFzoM5blXU0DiS9G4LyZVbYvLTgT0Bb5lGbXDRUfT05iLDfuaFc-PvR3s5PW2l8KoQap9HkV1T6YtgGzeptyjICjXUqpm4Ohb9blN2yJtxJyLOi6HLnY_OD153gnD0B_suo5kuojJhL3MshNQfhw94koSvIzcMqu1Mgnrz3rJY-ly9; csrftoken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjc3JmIjoiY3NyZl90b2tlbiIsImV4cCI6MTc2MDk5Mzk5NX0.ZJy6uCeNbdvJYfvl0mdghaFlJS_hKnwsBUQ-ur36hVw;"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())


__main__.py