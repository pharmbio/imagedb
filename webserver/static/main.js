var loaded_plate = null;

function removeChildren(domObject) {
    while (domObject.firstChild) {
        domObject.removeChild(domObject.firstChild);
    }
}

function getWellName(row, col){
  var rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"];
  return rows[row]  + col.toString().padStart(2,0)
}

function createMergeThumbImgURLFromChannels(channels){
  let url = "/api/image-merge-thumb/" + encodeURIComponent(JSON.stringify(channels))
  return url;
}

function createMergeImgURLFromChannels(channels){
  let url = "/api/image-merge/ch1/" + channels[1] + "/ch2/" + channels[2] + "/ch3/" + channels[3];
  return url;
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
  for(let row = 0; row < rows; row ++ ){
    let rowElement = document.createElement('tr');
    for(let col = 1; col <= cols; col ++){
      let well_name = getWellName(row, col);
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
    //console.log('well:' + well);

    let channels = plateObj[timepoint][well][wellsample];
    //console.log('channels:' + channels);

    let well_cell = document.getElementById(well);
    let imageCanvas = document.createElement('canvas');
    // Canvas size should not be set with css-style
    imageCanvas.width = 100; //well_cell.clientWidth;
    imageCanvas.height = 100; //well_cell.clientHeight;
    imageCanvas.className = 'plateImageCanvas';


    //well_div.appendChild(imageCanvas);
    well_cell.appendChild(imageCanvas);
    let context = imageCanvas.getContext('2d');

    let img = document.createElement('img');
    let url = createMergeThumbImgURLFromChannels(channels);
    img.src = url;
    img.className = 'plateThumbImg';

    img.onload = function () {
      context.drawImage(img, 0, 0);
    }

    let full_img_url = createMergeImgURLFromChannels(channels);
    imageCanvas.onclick = function(){ window.open("/image-viewer/" + full_img_url) }

  })
}

function getTimepoints(plateObj){
  // A plate-object is nothing but timepoints
  return plateObj;
}

function getSelectedTimepointIndex(){
  let elem =document.getElementById('timepoint-select');
  return elem.options[elem.selectedIndex].value;
}

function countTimepoints(plateObj){
  return Object.keys(getTimepoints(plateObj)).length;
}

function updateTimepointSelect(plateObj){

  elemSelect =  document.getElementById('timepoint-select');
  // reset
  elemSelect.options.length = 0;

  let nCount = countTimepoints(plateObj);
  for(let n = 0; n < nCount; n++){
    elemSelect.options[n] = new Option( n + 1 );
  }
}

function updateWellsampleSelect(plateObj){

  elemSelect =  document.getElementById('wellsample-select');
  // reset
  elemSelect.options.length = 0;

  let nCount = countWellsamples(plateObj);
  for(let n = 0; n < nCount; n++){
    elemSelect.options[n] = new Option( n + 1 );
  }
}

function updateChannelSelect(plateObj){

  elemSelect =  document.getElementById('channel-select');
  // reset
  elemSelect.options.length = 0;

  let nCount = countChannels(plateObj);

  //if(nCount > 1){
  elemSelect.options[0] = new Option( "Merge channels 1-3" );

  for(let n = 0; n < nCount; n++){
    elemSelect.options[n + 1] = new Option( n + 1 );
  }
}

function countChannels(plateObj){

  // Count number of keys for the first well of first Timepoint in plate object
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

function getSelectedChannelIndex(){
  let elem =document.getElementById('channel-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedTimepointIndex(){
  let elem =document.getElementById('timepoint-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedWellsampleIndex(){
  let elem =document.getElementById('wellsample-select');
  return elem.options[elem.selectedIndex].value;
}

function countWellsamples(plateObj){

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

function updateTimepointSelect(plateObj){

  tpSelect =  document.getElementById('timepoint-select');
  // reset
  tpSelect.options.length = 0;

  let nTimepoints = countTimepoints(plateObj);

  console.log(nTimepoints)

  for(let n = 0; n < nTimepoints; n++){
    tpSelect.options[n] = new Option( (n + 1).toString(), (n + 1).toString() );
  }
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
      updateTimepointSelect(window.loaded_plate)
      updateWellsampleSelect(window.loaded_plate)
      updateChannelSelect(window.loaded_plate)

      refreshPlate();

    })
    .catch(error => {
      console.error('Error:', error);
    })
}

function refreshPlate(){
      // get plate to draw
      let plateObj = window.loaded_plate;
      console.log(plateObj);

      // get timepoint to draw
      let timepoint = getSelectedTimepointIndex();

      // get wellsample to draw
      let wellsample = getSelectedWellsampleIndex();

      // let plateObj = response['data'].plates[plate];
      // console.log('plate:' + plateObj);

      drawPlate(plateObj, timepoint, wellsample);
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
