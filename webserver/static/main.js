var loaded_plate = null;

function removeChildren(domObject) {
    while (domObject.firstChild) {
        domObject.removeChild(domObject.firstChild);
    }
}

function getWellName(col, row){
  var cols = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"];
  return cols[col] + row.toString().padStart(2,0)
}


function getThumbURLFromChannels(channels){

  console.log(channels);

  channels_count = Object.keys(channels).length;

  let url = "";
  if(channels_count >= 3){
    url = getMergeImgURLFromChannels(channels);
  }
  else{
    // Get first channel thumbnail
    url = channels['1'];

  }

  return url;

}

function getMergeImgURLFromChannels(channels){

  console.log("channels:");
  console.log(channels);

  fetch('/api/image-merge', {
      method : 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(channels), // body data type must match "Content-Type" header
  })
    .then((res) => res.json())
    .then((data) =>  console.log(data))
    .catch((err)=> console.error('Error:', error));

}

function createMergeImgURLFromChannels(channels){
  let url = "/api/image-merge/" + encodeURIComponent(JSON.stringify(channels))
  return url;
}

function refreshPlate(){
      // get plate to draw
      let plateObj = window.loaded_plate;
      console.log(plateObj);

      // get timepoint to draw
      let timepoint = document.getElementById('timepoint-field').value;

      // get wellsample to draw
      let elem = document.getElementById("wellsample-field");
      let wellsample = elem.options[elem.selectedIndex].value;

      // let plateObj = response['data'].plates[plate];
      // console.log('plate:' + plateObj);

      drawPlate(plateObj, timepoint, wellsample);
}

function drawPlate(plateObj, timepoint, wellsample){

  console.log(plateObj);

  let container = document.getElementById('table-div');
  removeChildren(container);

  // first create a new plate consisting of empty well-div's
  let rows = 8;
  let cols = 12;
  let table = document.createElement('table');
  table.className = 'plateTable';
  container.appendChild(table);
  for(let row = 1; row <= rows; row ++ ){
    let rowElement = document.createElement('tr');
    for(let col = 0; col < cols; col ++){
      let well_name = getWellName(col, row);
      let well_cell = document.createElement('td');
      well_cell.id = well_name;
      rowElement.appendChild(well_cell);
    }
    table.appendChild(rowElement);
  }

  console.log(container);
  console.log('done create div');
  console.log('plate:' + plateObj);

  // now populate well-div's with the plateObj contents
  Object.keys(plateObj[timepoint]).forEach(well => {
    console.log('well:' + well);

    let channels = plateObj[timepoint][well][wellsample];
    console.log('channels:' + channels);
    let well_cell = document.getElementById(well);
    let imageCanvas = document.createElement('canvas');
    // Canvas size should not be set with css-style
    imageCanvas.width = well_cell.clientWidth;
    imageCanvas.height = well_cell.clientHeight;
    imageCanvas.className = 'plateImageCanvas';

    //well_div.appendChild(imageCanvas);
    well_cell.appendChild(imageCanvas);
    let context = imageCanvas.getContext('2d');

    let img = document.createElement('img');
    let url = createMergeImgURLFromChannels(channels);
    img.src = url;
    img.className = 'plateThumbImg';

    img.onload = function () {
      context.drawImage(img, 0, 0);
    }

  })
}

function loadPlate(plate_name) {

  fetch('/api/list/' + plate_name)
    .then(response => response.json())
    .then(response => {

      window.loaded_plate = response['data'].plates[plate_name];
      console.log(window.loaded_plate);

      // TODO set title when plate object contains that also!
      //document.getElementById('plate-name-title').value = window.loaded_plate.plate;
      // TODO add project also?


      refreshPlate();

    })
    .catch(error => {
      console.error('Error:', error);
    })
}


function loadImageThing(plate) {

    fetch('/api/list/' + plate)
        .then(response => response.json())
        .then(response => {
            let container = document.getElementById('table-div');
            removeChildren(container);

            // create a new plate consisting of well-div
            let rows = 8;
            let cols = 12;
            let sites = 1;

            let table = document.createElement('table');
            table.className = 'plateTable';
            container.appendChild(table);

            for(let row = 1; row <= rows; row ++ ){
              let rowElement = document.createElement('tr');
              //rowElement.className = 'imageRow';
              for(let col = 0; col < cols; col ++){
                let well_name = getWellName(col, row);
                let well_cell = document.createElement('td');
                well_cell.id = well_name;
                //well_cell.width = "50";
                //well_cell.height = "50";
                //console.log(well_name);
                rowElement.appendChild(well_cell);
              }
              table.appendChild(rowElement);
            }

            console.log(container);

            console.log('done create div');
            console.log(response);
            let plates = response['data'].plates;

            Object.keys(plates).forEach(plate => {
              console.log('plate:' + plate);

              Object.keys(plates[plate]).forEach(timepoint => {
                console.log('timepoint:' +  timepoint);

                 if("0" != timepoint && "1" != timepoint){
                   return;
                 }

                 Object.keys(plates[plate][timepoint]).forEach(well => {
                   console.log('well:' + well);

                  Object.keys(plates[plate][timepoint][well]).forEach(wellsample => {
                    console.log('wellsample:' + wellsample);

                    let channels = plates[plate][timepoint][well][wellsample];
                    let well_cell = document.getElementById(well);
                    let imageCanvas = document.createElement('canvas');
                    // Canvas size should not be set with css-style
                    imageCanvas.width = well_cell.clientWidth;
                    imageCanvas.height = well_cell.clientHeight;
                    imageCanvas.className = 'plateImageCanvas';

                    //well_div.appendChild(imageCanvas);
                    well_cell.appendChild(imageCanvas);

                    drawChannelsOnCanvas(channels);
                    /*
                    getThumbURLFromChannels(channels);

                    let context = imageCanvas.getContext('2d');
                    let img = document.createElement('img');
                    let url = getThumbURLFromChannels(channels);
                    img.src = url;
                    img.className = 'plateThumbImg';

                    function loop() {
                      context.drawImage(img, 0, 0);
                    }
                    let loopVar = setInterval(loop, 1000);
                    */



  /*
                    Object.keys(plates[plate][timepoint][well][wellsample]).forEach(channel => {
                      console.log('channel' + channel);
                      console.log('path=' + plates[plate][timepoint][well][wellsample][channel]);

                      //  if(channel == 0){
                      //    var path = plates[plate][timepoint][well][wellsample][channel];
                      //    var img = document.createElement('img');
                      //    img.className = 'plateThumbImg';
                      //    img.src = path;
                      //    //img.width = "70";
                      //    //img.height = "70";
                      //    let well_div = document.getElementById(well);
                      //    well_div.appendChild(img);
                      //  }

                          let well_cell = document.getElementById(well);
                          //let well_div = document.createElement('div');
                          //well_div.className = 'imageContainer';

                          var imageCanvas = document.createElement('canvas');
                          // Canvas size should not be set with css-style
                          imageCanvas.width = well_cell.clientWidth;
                          imageCanvas.height = well_cell.clientHeight;
                          imageCanvas.className = 'plateImageCanvas';

                          //well_div.appendChild(imageCanvas);
                          well_cell.appendChild(imageCanvas);
                          var context = imageCanvas.getContext('2d');

                          var img = document.createElement('img');
                          var path = plates[plate][timepoint][well][wellsample][channel];
                          img.src = path;
                          img.className = 'plateThumbImg';

                          function loop() {
                            context.drawImage(img, 0, 0);
                          }
                          var loopVar = setInterval(loop, 1000);
                    })
                  */
                  })
                })

              })

            })
/*

            // Now populate well-divs with canvas and images
            response['data'].forEach(image => {
                var imageContainer = document.getElementById(image.metadata.well
                rowElement.className = 'imageRow';
                var imageCanvas = document.createElement('canvas');
                imageContainer.className = 'imageContainer';
                imageContainer.appendChild(imageCanvas);

                var context = imageCanvas.getContext('2d');
                // load all images
                var images = [];
                bundle.forEach(image => {
                  var img = document.createElement('img');
                  img.src = '/api/image/' + image;
                  images.push(img);
                })
                container.appendChild(rowElement);
                row.forEach(bundle => {
                    var imageContainer = document.createElement('div');
                    var imageCanvas = document.createElement('canvas');
                    imageContainer.className = 'imageContainer';
                    imageContainer.appendChild(imageCanvas);

                    var context = imageCanvas.getContext('2d');
                    // load all images
                    var images = [];
                    bundle.forEach(image => {
                        var img = document.createElement('img');
                        img.src = '/api/image/' + image;
                        images.push(img);
                    })

                    var current = -1;

                    function loop() {
                        if (++current >= images.length) {
                            current = 0;
                        }
                        context.drawImage(images[current], 0, 0);
                    }
                    //var loopVar = setInterval(loop, 1000);

                    rowElement.appendChild(imageContainer);
                })
            });
            */
        })
        //.catch(error => console.error('Error:', error));

}

function apiQuery(event) {
    event.preventDefault();

    fetch('/api/query', {
        method : 'POST',
        body: new FormData(document.getElementById('query-form'))
    })
    .then(response => response.json())
    .then(response => {
        console.log(response)
        console.log(response.results)
        let list = document.getElementById('result-list');
        removeChildren(list);
        response.results.forEach(element => {
            console.log('element' + element)
            let child = document.createElement('li');
            let link = document.createElement('a');
            link.href = "";
            let linktext = '' + element._id.project + " - " + element._id.plate;
            let content = document.createTextNode(linktext);
            link.appendChild(content);
            child.appendChild(link);

            child.onclick = function(e) {
                e.preventDefault();
                loadPlate(element._id.plate)
            };

            list.appendChild(child);
        })
    })
    .catch(error => console.error('Error:', error));
}
