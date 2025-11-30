# rfi-matcher
Extract potential sources of RFI in public observations for a given frequency band, time duration and beam interval.

## Filtering
The code allows you to crawl observatory data archives based on the observatories filtered by creating an `ra_filter.RaFilter` object:
- Frequency Band (c.f. `ra_filter.set_frequencies()`)
- Time Duration (c.f. `ra_filter.set_start_time()`and `ra_filter.set_end_time()`)
- Area of Interest (c.f. `ra_filter.set_latitude()` and `ra_filter.set_longitude()`)

You may also already select a specific list of observatories of interest with `ra_filter.set_observatories()`.

## Output
After running the *rfi-matcher.py* script, the code creates a *rfi_data.csv* file in the *data/* folder.

The resulting file contains the following columns:
- **name**: name of observatory
- **observation_id**: observation's unique identifier (data archive-specific) 
- **frequency**: center frequency of the observation
- **bandwidth**
- **declination**: observed target declination in DMS (degrees-minutes-seconds) format
- **right_ascension**: observed target right ascension in HMS (hours-minutes-seconds) format 
- **begin**: observation start ISO time
- **end**: observation end ISO time
- **url**: link to data of observation
- **NORAD**: list of RFI satellites per observation and their closest proximity timestamp, coordinates and angular distance
