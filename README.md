# Earth Yesterday
_A simple application that creates a video of yesterday's "Blue Marble" images of Earth_

## Architecture
1. Image Fetcher
  - Pulls images and metadata, from [NASA API](https://epic.gsfc.nasa.gov/about/api), for images produced yesterday (if any)
  - Dowloads the images and metadata
  - Sends message over RabbitMQ to renderer
2. Video Renderer
  - When RMQ message is received
  - Reads the metadata and validates that images are ready to be rendered
  - Uses ffmpeg to render a video
3. Web Application
  - Serves the videos on a web page
