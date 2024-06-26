# A Video of Earth and (nearly) Everyone Yesterday (AVEEY)
_A simple application that creates a video of Earth and an accounting of who is in the video and who is not_

## What is this?
This project is for the curious. It is intended to provide a unique and not-so-serious web page that shows a video of earth as it was yesterday (or the most recent set of images from DSCOVR), along with an accounting of who was in the video, and who was not. I hope it sparks rumination and a smirk for those that view it. By its very nature, it will be inaccurate, and therefor should not be viewed by pedants

The famous [Blue Marble](https://en.wikipedia.org/wiki/The_Blue_Marble) photograph of earth from 1972 gave a perspective of the planet where (nearly) all humans live. But that was in 1972. What did earth look like yesterday from space? And who was on that earth? Using images captured from [The Deep Space Climate Observatory](https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/dscovr-deep-space-climate-observatory), and population estimates for both earth and space, we can answer those questions.

## High Level Architecture
[Architecture Diagram](./architecture-diagram.md)
- Data Fetcher
  - Pulls metadata, from [NASA API](https://epic.gsfc.nasa.gov/about/api), for images produced yesterday, or the most recently available
  - Downloads images and saves them to an AWS S3 bucket
  - Pulls world population estimates for the day images were produced from [US Census](https://www.census.gov/popclock)
  - Pulls space population data from [Open Notify](http://open-notify.org/Open-Notify-API/People-In-Space/)
    - This API returns who is in space at time of the request, so it will be saved along with a time stamp to be used in future calculations
  - Saves population data image metadata to Postgres Database
  - Sends message over RabbitMQ (RMQ) with information about images that are to be processed
- Data Processor
  - When RMQ message is received
    - Render video
      - Reads the images from the DB (based on RMQ message)
      - Uses ffmpeg to render a video of the images
      - Saves the video to a publicly available S3 Bucket
    - Calculates who is in the video, and who is not :)
      - Reads population of earth and space data from the DB
      - Calculates who was on earth, and who was not
    - Updates the DB with a new row with video link, and associations with the population tables
- Web Application
  - Serves a simple web page
  - Pulls video and population data from the DB
  - Uses the public s3 bucket to serve the video to the user

### Design Decisions
- Postgres was chosen because there are relationships between several of the data models, and the structure of the data was well understood, so a relational database fit this use-case nicely
- The Data Fetcher was deployed to wake up every day and check the APIs for new data, reducing the resource usage and cost compared to a continuously running service.
- The Data Processor is loosely coupled to both the data fetcher and the web application, via a messaging queue and database, allowing for a more focused service, and even opening up the possibility of parallelizing the CPU intensive video interpolation task
- RabbitMQ was selected as the messaging queue implementation because of its availability and wealth of features.

## Project Rubric
_Addressing grading rubric for CU Boulder CSCA5028_

- Web application basic form, reporting
  - See the deployed web application and source code for details of the web app
- Data collection
  - The `data_fetcher` is the collection service that goes out to three different APIs to gather data
- Data analyzer
  - The `data_processor` is what analyzes the data gathered, creating a video from the images, and calculating the population numbers
- Unit tests
  - There are unit tests for the data_fetcher, see `test_nasa_epic.py`, `test_space_pop.py`, and `test_world_pop.py`
- Data persistence any data store
  - Image and video data is persisted in AWS S3 buckets, and metadata is stored in a Postgres Database
- Rest collaboration internal or API endpoint
  - Three different APIs are used gather data
- Production environment
  - The project as a whole is deployed on Heroku, and the web app is publicly available
- Integration tests
  - There is an integration test that runs the data_fetcher, going out to the actual APIs, and saving to S3 and the DB. And then the processor is envoked, reading from the DB and S3, calling ffmpeg to create the video, and then persisting the processed data in S3 and the DB. This integration test was invaluable while I was developing and debugging this project
- Using mock objects or any test doubles
  - I used mocks in the unit tests, and leveraged the [responses](https://github.com/getsentry/responses) utility to mock the API calls. This allowed me to not have to rely on real network calls for the unit tests, so they were faster and I was able to control the test conditions
- Continuous integration
  - A GitHub action was used to run linting and unit tests automatically. Every time a commit was merged to the `main` branch, the code was linted and the unit tests were run
- Production monitoring instrumenting
  - Simple image and video processing metrics are exposed via a `metrics` endpoint on the Web app
- Event collaboration messaging
  - RabbitMQ messsages were used for coordination between the data fetcher and the data processor. The fetcher produced an event when images were ready to be processed, and the processor listened for that event to start processing
- Continuous delivery
  - Heroku was used to automatically deploy all three parts of the project (fetcher, processor, and web app). It was configured to wait until the unit tests, that the CI implemented with GitHub Actions was running, all passed, then it pulls the updated data, builds the services, provisions the nodes, and then deploys the application. Near the end of this project, it was very helpful to have this CI/CD pipeline setup so as I fixed bugs, I knew all I needed to do was push to the `main` branch, and if the tests passed, the change would go to production
