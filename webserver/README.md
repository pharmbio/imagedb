# webserver/GUI - imagedb

## Features
- The main purpose of the Image database GUI component is to easily inspect and get an overview of plate images.
- Navigation of plates is done in a project-plate-acquisition hierarchy.
- The initial plate overview visualizes a full 96 or 384 well plate.
- The plate overview can display either a specific single site per well or all imaged sites of all wells at once.
- In multi channel images either channel image can be viewed individually or three channels merged together each channel assigned red, green or blue color.
- From the overview any site image can be opened at original size in an embedded zoomable image viewer component.
- Animation of image time series both in plate overview and single full size image. 
- Analyses done from the Cp-pipeline are linked and presented in a table connected to the plate being viewed.
## Implementation
- Python Tornado web server backend
- Javascript and HTML frontend utilizing Bootstrap 4 for layout and theming of components.
- Embedded OpenSeadragon javascript image viewer. 
- Dockerized deployment.



```
# Run with docker-compose
# Development settings are in .env
docker-compose up

https://imagedb.devserver.pharm.io

# Build dockerfile
docker build -t pharmbio/imagedb-webserver .

# Push
docker login
docker push pharmbio/imagedb-webserver

```

