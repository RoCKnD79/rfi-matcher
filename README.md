# rfi-matcher
Extract potential sources of RFI in public observations for a given frequency band, time duration and beam interval.

## Prerequisites
The package fetches TLE data from [Space-Track.org](https://www.space-track.org). 
For this to work, please declare **environment variables** `ID_SPACE_TRACK` and `PWD_SPACE_TRACK` on your system in your current terminal instance, by running:
- `export ID_SPACE_TRACK=<your_space_track_id>`
- `export PWD_SPACE_TRACK=<your_space_track_password>`

You can also add the two lines in your `~/.bashrc` file for the variables to be declared at **each new terminal instantiation**.

## Filtering
The code allows you to crawl observatory data archives based on the observatories filtered by creating an `ra_filter.RaFilter` object. 
The object allows you to set the following parameters:
- Frequency Band (c.f. `ra_filter.set_frequencies()`)
- Time Duration (c.f. `ra_filter.set_start_time()`and `ra_filter.set_end_time()`)
- Area of Interest (c.f. `ra_filter.set_latitude()` and `ra_filter.set_longitude()`)

You may also already select a specific list of observatories of interest with `ra_filter.set_observatories()`.

## Output
Running the entire pipeline results in a *rfi_data.csv* file in the *data/* folder.

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


## Setting up the Environment
Please take a look at the `examples` folder for an example **jupyter notebook** or **python script**.

In terminal:
1. Create a virtual python environment at directory root level: `python3 -m venv venv` 
2. Activate the venv `. venv/bin/activate` and install all required dependencies `pip install -r requirements.txt`
3. Enter directory *rfi-matcher/examples/* by running `cd rfi-matcher/examples` in terminal 
4. Run `python3 get-rfi.py`


## Third-Party Tools
- **S.O.P.P. - Satellite Orbit Prediction Processor:** [SOPP](https://github.com/NSF-Swift/satellite-overhead) is an open-source tool for calculating satellite interference to radio astronomy observations. RFI-Matcher uses SOPP extensively to build the list of potential satellite RFI sources for each observation collected from data archives.
- **Space-Track:** [Space-Track.org](https://www.space-track.org) is a site maintained by the U.S. Space Force that allows users to query a database and download satellite TLEs. SOPP contains the functionality to pull satellite TLEs from Space-Track for use in the program, but the site requires users to have an account.
- **Rhodesmill Skyfield:** The [Skyfield API](https://rhodesmill.org/skyfield/) is a comprehensive Python package for computing the positions of stars, planets, and satellites. SOPP uses the Skyfield API to find all the satellites visible above the horizon during an observation search window.
- **Satellite Frequencies:** a satellite frequency database was created by scraping frequency information from various open sources. The code used to generated the database can be found [here](https://github.com/NSF-Swift/sat-frequency-scraper).
