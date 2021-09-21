# SLDMB Data

Data is available from http://sldmb.ca. Contact Graig with regards to obtaining a username and password.

These drifters are deployed irregularly by the CCG during SAR operations. The sldmb is similar to the CODE-DAVIS drifters, although I believe the drogue is a slightly different dimension.

The data is in the form of a pickled pandas dataframe. The index is the unique drifter identififier (drifter\_ID) which has the format:
- buoyname\_yyyymmddHHMMSS\_yyyymmddHHMMSS where the first date is track start time and the second date is track end time. This is because the CCG often reuses the same drifter for later deployments. 

As of the writing of this (Sep 2021) there has been no quality control or processing of the raw data.

Also, the data is periodically updated, and I do have a crude script to scrape the data, but it is most likely easier to check the website from time to time and export the newer tracks. I can share the webscraper script if there is interest.
