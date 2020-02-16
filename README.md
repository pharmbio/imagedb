# AROS image, project, data, metadata and lab automation system database.
Currently this repo contains both the actual postgres database and the Web-GUI Image Viewer but will soon be split into two separate repos, one for the Database and one for the Web Interface.

# Repo structure:

  /cli - command line tool for importing, monitoring, image conversion etc.

  /db - postgresdb setup with docker-compose

  /share - demo data

  /webserver - tornado python webserver, web-api and image-viewer-webclient
  
  ![Imagedb screenshot](https://raw.githubusercontent.com/pharmbio/imagedb/master/screenshot.jpg)
  
  
  ![Imagedb screenshot](https://raw.githubusercontent.com/pharmbio/imagedb/master/screenshot_viewer.jpg)
  
  
