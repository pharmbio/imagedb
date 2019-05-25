/*
  Javascript version: ECMAScript 6 (Javascript 6)
 */

var loaded_plate = null;

function removeChildren(domObject) {
  while (domObject.firstChild) {
    domObject.removeChild(domObject.firstChild);
  }
}

function getWellName(row, col) {
  var rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"];
  return rows[row] + col.toString().padStart(2, 0)
}

function createMergeThumbImgURLFromChannels(channels) {
  let url = "/api/image-merge-thumb/" + encodeURIComponent(JSON.stringify(channels));
  return url;
}

function createMergeImgURLFromChannels(channels) {
  let url = "/api/image-merge/ch1/" + channels[1] + "/ch2/" + channels[2] + "/ch3/" + channels[3];
  return url;
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
          updateTimepointSelect(window.loaded_plate);
          updateTimepointSlider(window.loaded_plate);
          updateWellsampleSelect(window.loaded_plate);
          updateChannelSelect(window.loaded_plate);

          drawNewPlate();

        })
        .catch(error => {
          console.error('Error:', error);
        })
}

function drawNewPlate(){
  redrawPlate(true);
}

function redrawPlate(clearFirst=false) {
  // get plate to draw
  let plateObj = window.loaded_plate;

  // get timepoint to draw
  let timepoint = getSelectedTimepointIndex();

  // get wellsample to draw
  let wellsample = getSelectedWellsampleIndex();

  drawPlate(plateObj, timepoint, wellsample, clearFirst);
}

function drawPlate(plateObj, timepoint, wellsample, clearFirst) {

  console.log(plateObj);

  let container = document.getElementById('table-div');

  if(clearFirst){
    removeChildren(container);
  }

  // first create a new plate consisting of empty well-div's
  // TODO fix for other plate sizes
  let rows = 8;
  let cols = 12;
  if (document.getElementById('plateTable') == null) {

    let table = document.createElement('table');
    table.id = 'plateTable';
    table.className = 'plateTable';
    container.appendChild(table);

    for (let row = 0; row < rows; row++) {
      let rowElement = document.createElement('tr');
      for (let col = 1; col <= cols; col++) {
        let well_name = getWellName(row, col);
        let well_cell = document.createElement('td');
        well_cell.id = well_name;
        rowElement.appendChild(well_cell);
      }
      table.appendChild(rowElement);

    }
  }

  console.log(container);
  console.log('done create div');
  console.log('plate:' + plateObj);

  // now populate well-div's with the plateObj contents
  Object.keys(plateObj[timepoint]).forEach(well => {

    let channels = plateObj[timepoint][well][wellsample];
    //console.log('channels:' + channels);

    let well_cell = document.getElementById(well);

    // Try to get existing canvas - if it doesn't exist create it
    let wellCanvas = document.getElementById('wellCanvas' + well);
    if (wellCanvas == null) {

      wellCanvas = document.createElement('canvas');
      wellCanvas.className = 'wellCanvas';
      wellCanvas.id = 'wellCanvas' + well;

      // TODO fix resizing of canvas
      // Canvas size should not be set with css-style
      wellCanvas.width = 100;
      wellCanvas.height = 100;

      well_cell.appendChild(wellCanvas);
    }

    let context = wellCanvas.getContext('2d');
    let url = createMergeThumbImgURLFromChannels(channels);
    let img = document.createElement('img');
    img.src = url;
    img.className = 'wellThumbImg';
    img.id = 'wellThumbImg' + well;

    img.onload = function () {
      context.drawImage(img, 0, 0);
    }

    // Create full image links for opening viewer
    let fullImg_url = createMergeImgURLFromChannels(channels);
    wellCanvas.onclick = function () {
      openViewer(fullImg_url);
    }

  })
}


function openViewer(imageURL) {
  window.open("/image-viewer/" + imageURL);
}

function openViewerInMainDiv(imageURL) {

  let container = document.getElementById('table-div');
  removeChildren(container);

  var viewer = OpenSeadragon({
    id: "table-div",
    prefixUrl: "/static/openseadragon/images/",
    animationTime: 0.5, // default 1.2
    zoomPerSecond: 1, // default: 1
    zoomPerScroll: 1.7, // default: 1.2
    minZoomImageRatio: 0.9, // default: 0.8
    maxZoomPixelRatio: 10,  // deault: 2
    tileSources: {
      type: 'image',
      url: imageURL,
      buildPyramid: false
    }
  });

}


function getSelectedTimepointIndex() {
  let elem = document.getElementById('timepoint-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedChannelIndex() {
  let elem = document.getElementById('channel-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedWellsampleIndex() {
  let elem = document.getElementById('wellsample-select');
  return elem.options[elem.selectedIndex].value;
}


function updateTimepointSelect(plateObj) {

  elemSelect = document.getElementById('timepoint-select');

  // reset
  elemSelect.options.length = 0;

  // add as many options as timepoints
  let nCount = countTimepoints(plateObj);
  for (let n = 0; n < nCount; n++) {
    elemSelect.options[n] = new Option(n + 1);
  }
}


function updateTimepointSlider(plateObj) {

  let nCount = countTimepoints(plateObj);

  // disable if single timepoint
  if (nCount == 1) {
    disable = true;
  } else {
    disable = false;
  }

  // Get slider function
  let slider = $("#timepoint-slider").data("ionRangeSlider");

  // update
  slider.update({
    min: 1,
    max: nCount,
    disable: disable
  });

}


function updateWellsampleSelect(plateObj) {

  elemSelect = document.getElementById('wellsample-select');

  // reset
  elemSelect.options.length = 0;

  // add as many options as wellsamples
  let nCount = countWellsamples(plateObj);
  for (let n = 0; n < nCount; n++) {
    elemSelect.options[n] = new Option(n + 1);
  }
}

function updateChannelSelect(plateObj) {

  elemSelect = document.getElementById('channel-select');

  // reset
  elemSelect.options.length = 0;

  let nCount = countChannels(plateObj);

  // First add default (Merge channels options)
  elemSelect.options[0] = new Option("Merge channels 1-3");

  // add as many options as channels
  for (let n = 0; n < nCount; n++) {
    elemSelect.options[n + 1] = new Option(n + 1);
  }
}

function countTimepoints(plateObj) {

  // A plate-object is nothing but a dict of timepoints
  let timepoints = plateObj;
  // Count number of keys in timepoint object
  return Object.keys(timepoints).length;
}

function countChannels(plateObj) {

  // Count number of keys for the first wellsample of first well of first Timepoint in plate object
  nCount = 0;
  looplabel:
        Object.keys(plateObj).every(timepoint => {
          console.log('timepoint:' + timepoint);
          Object.keys(plateObj[timepoint]).every(well => {
            console.log('well:' + well);
            Object.keys(plateObj[timepoint][well]).every(wellsample => {
              // The wellsample object contains a dict of channels
              nCount = Object.keys(plateObj[timepoint][well][wellsample]).length;
              return nCount;
            })
          })
        })

  return nCount;
}

function countWellsamples(plateObj) {

  // Count number of keys for the first well of first Timepoint in plate object
  nCount = 0;
  looplabel:
        Object.keys(plateObj).every(timepoint => {
          console.log('timepoint:' + timepoint);
          Object.keys(plateObj[timepoint]).every(well => {
            console.log('well:' + well);
            // The well object contains a dict of wellsamples
            nCount = Object.keys(plateObj[timepoint][well]).length;
            return nCount;
          })
        })

  return nCount;
}


function apiQuery(event) {
  event.preventDefault();

  fetch('/api/query', {
    method: 'POST',
    body: new FormData(document.getElementById('query-form'))
  })
        .then(response => response.json())
        .then(response => {
          console.log(response)
          console.log(response.results)
          let list = document.getElementById('result-list');
          removeChildren(list);
          let last_proj = "";
          let plate_list = null;
          response.results.forEach(result => {
            /*
                       <ul id='result-list'>
                        <li>ACN92</li>
                          <ul>
                            <li><a href="#" class="">P0023</a></li>
                            <li><a href="#" class="">P0023</a></li>
                          </ul>
                        <li>EXP28</li>
                           <ul>
                             <li>Gadgets</li>
                             <li>Accessories</li>
                           </ul>
                       </ul>
            */
            let proj = result._id.project;
            let plate = result._id.plate;

            // create a new sublist for each project
            if (last_proj != proj) {
              let proj_item = document.createElement('li');
              proj_item.innerHTML = proj;
              list.appendChild(proj_item);
              plate_list = document.createElement('ul');
              proj_item.appendChild(plate_list);
            }

            let plate_item = document.createElement('li');
            let link = document.createElement('a');
            link.href = "";
            let linktext = plate;
            let content = document.createTextNode(linktext);
            link.appendChild(content);
            plate_item.appendChild(link);

            plate_item.onclick = function (e) {
              e.preventDefault();
              loadPlate(plate)
            };

            plate_list.appendChild(plate_item);
            last_proj = proj;
          })
          console.log("Before tree-call")

          jQuery('#result-list').fancytree();


          ;
        })
        .catch(error => console.error('Error:', error));
}
