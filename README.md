# A Video of Earth and (nearly) Everyone Yesterday (AVEEY)
_A simple application that creates a video of Earth and an accounting of who is in the video and who is not_

## What is this?
This project is for the curious. It is intended to provide a unique and not-so-serious web page that shows a video of earth as it was yesterday (or the most recent set of images from DSCOVR), along with an accounting of who was in the video, and who was not. I hope it sparks rumination and a smirk for those that view it. By its very nature, it will be inaccurate, and therefor should not be viewed by pedants

The famous [Blue Marble](https://en.wikipedia.org/wiki/The_Blue_Marble) photograph of earth from 1972 gave a perspective of the planet where (nearly) all humans live. But that was in 1972. What did earth look like yesterday from space? And who was on that earth? Using images captured from [The Deep Space Climate Observatory](https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/dscovr-deep-space-climate-observatory), and population estimates for both earth and space, we can answer those questions.

## High Level Architecture
[Architecture Diagram](./architecture-diagram.md)
- Data Fetcher
  - Pulls metadata, from [NASA API](https://epic.gsfc.nasa.gov/about/api), for images produced yesterday (if any)
  - Downloads images and saves them to data volume
  - Pulls world population estimates for the day images were produced from [WorldPop](https://www.worldpop.org/sdi/introapi/)
  - Pulls space population data from [Open Notify](http://open-notify.org/Open-Notify-API/People-In-Space/)
    - This API returns who is in space at time of the request, so it will be saved along with a time stamp to be used in future calculations
  - Saves population data and path images to DB
  - Sends message over RabbitMQ to initiate rendering
- Data Processor
  - When RMQ message is received
    - Renders video
      - Reads the most recent set of images from the DB
      - Uses ffmpeg to render a video from the images
      - Saves the video to the data volume
    - Calculates who is in the video, and who is not
      - Reads population of earth and space data from DB
      - Calculates who was on earth, and who was not
    - Updates the DB record with path to video and population calculation
- Web Application
  - Serves a simple web page
  - API for videos and associated population
