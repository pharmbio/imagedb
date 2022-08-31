/*
  Javascript version: ECMAScript 6 (Javascript 6)
 */
class Plates {
  constructor(jsondata) {
    this.jsondata = jsondata;
  }

  getPlate(index) {
    // return first (and only) plate
    return new Plate(this.jsondata[Object.keys(this.jsondata)[index]])
  }

  getFirstPlate() {
    return this.getPlate(0);
  }
}

class Plate {
  constructor(jsondata) {
    this.plateObj = jsondata;
  }

  getName() {
    return this.plateObj.id;
  }


  getPlateSize(siteNames) {
    // Loop through wellNames (for all acquisitions) and see if size is outside 96 or 384 plate limit
    // if not return 96, 384 or 1536

    Object.keys(this.plateObj.acquisitions)

    let nMaxRow = 1
    let nMaxCol = 1

    for(let acquisition_id of Object.keys(this.getAcquisitions())){
      let wells = this.getWells(acquisition_id);
      for (let well of Object.values(wells)) {
        let wellName = well.id;

        let nRow = getRowIndexFrowWellName(wellName);
        let nCol = getColIndexFrowWellName(wellName);

        nMaxRow = Math.max(nMaxRow, nRow);
        nMaxCol = Math.max(nMaxCol, nCol);
      }
    }

    if (nMaxRow > 16 || nMaxCol > 26) {
      console.log("1536");
      return { "rows": 32, "cols": 48, "sites": siteNames };
    }

    if (nMaxRow > 8 || nMaxCol > 16) {
      console.log("384");
      return { "rows": 16, "cols": 24, "sites": siteNames };
    }

    console.log("96");
    return { "rows": 8, "cols": 12, "sites": siteNames };
  }

  getAvailableSites(acquisition_id) {
    // get names of the sites of the first acquisition and first well
    let firstPlateAcqKey = Object.keys(this.plateObj.acquisitions)[0];
    let firstWellKey = Object.keys(this.plateObj.acquisitions[firstPlateAcqKey].wells)[0];
    let sites = this.plateObj.acquisitions[firstPlateAcqKey].wells[firstWellKey].sites;

    let siteNames = [];
    for (let site of Object.values(sites)) {
      siteNames.push(site.id);
    }
    return siteNames;
  }

  getChannelNames(acquisition_id) {
    // Get channel keys for the first sites object of the first well of first acquisition in plate object
    let nCount = 0;
    let firstWellKey = Object.keys(this.plateObj.acquisitions[acquisition_id].wells)[0];
    let firstSiteKey = Object.keys(this.plateObj.acquisitions[acquisition_id].wells[firstWellKey].sites)[0];
    let channelNames = Object.keys(this.plateObj.acquisitions[acquisition_id].wells[firstWellKey].sites[firstSiteKey].channels);
    return channelNames;
  }

  getChannels(acquisition_id, well_name, site) {
    if(this.plateObj.acquisitions[acquisition_id] != null &&
       this.plateObj.acquisitions[acquisition_id].wells[well_name] != null &&
       this.plateObj.acquisitions[acquisition_id].wells[well_name].sites[site]){
      return this.plateObj.acquisitions[acquisition_id].wells[well_name].sites[site].channels;
    }
    else{
      return null;
    }
  }

  getWells(acquisition_id) {
    return this.plateObj.acquisitions[acquisition_id].wells;
  }


  getAcquisitions() {
    return this.plateObj.acquisitions;
  }

  countAcquisitions() {
    // Count number of acquisitions keys for the Plate object
    let nCount = 0;
    nCount = Object.keys(this.plateObj.acquisitions).length;

    return nCount;
  }

  countChannels(acquisition_id) {
    // Count number of keys for the first sites object of the first well of first acquisition in plate object
    let nCount = 0;
    let firstWellKey = Object.keys(this.plateObj.acquisitions[acquisition_id].wells)[0];
    let firstSiteKey = Object.keys(this.plateObj.acquisitions[acquisition_id].wells[firstWellKey].sites)[0];
    nCount = Object.keys(this.plateObj.acquisitions[acquisition_id].wells[firstWellKey].sites[firstSiteKey].channels).length;

    return nCount;
  }


  countWells() {
    // Count number of keys for the Wells object  of the first acquisition in plate object
    let nCount = 0;
    let firstPlateAcqKey = Object.keys(this.plateObj.acquisitions)[0];
    nCount = Object.keys(this.plateObj.acquisitions[firstPlateAcqKey].wells).length;

    return nCount;
  }

  countSites() {
    // Count number of keys for the sites object of the first well of first acquisition in plate object
    let nCount = 0;
    let firstPlateAcqKey = Object.keys(this.plateObj.acquisitions)[0];
    let firstWellKey = Object.keys(this.plateObj.acquisitions[firstPlateAcqKey].wells)[0];
    nCount = Object.keys(this.plateObj.acquisitions[firstPlateAcqKey].wells[firstWellKey].sites).length;

    return nCount;
  }

  getWellImageMeta(acquisition, well_name) {
    let imageMeta = this.plateObj.acquisitions[acquisition].wells[well_name].sites["1"].channels["1"].image_meta;
    return imageMeta;
  }

  getFormattedWellMeta(acquisition, well_name) {
    let well_image_meta = this.getWellImageMeta(acquisition, well_name);
    let formatted_meta = '';
    formatted_meta += "Well: " + this.plateObj.acquisitions[acquisition].wells[well_name].id + "<br>";
    formatted_meta += "Plate_barcode: " + well_image_meta["plate_barcode"] + "<br>";
    formatted_meta += "Plate_acq_id: " + acquisition + "<br>" + "<br>";
    return formatted_meta;
  }
}

var loaded_plates = null;
var animation = null;

function initMainWindow(plateBarcode, acquisitionID) {
  selectBrightnessFromStoredValue();
  selectHideUnpublishedFromStoredValue();
  apiListPlates();

  console.log("plateBarcode", plateBarcode);

  if (plateBarcode == "" && acquisitionID == "") {
    console.log("plateBarcode == '' && acquisitionID == '', Do nothing");
    // Do nothing
  } else if (acquisitionID != "") {
    apiLoadAcquisitionID(acquisitionID);
  } else {
    apiLoadPlateBarcode(plateBarcode);
  }
}

function initViewerWindow(){
  selectBrightnessFromStoredValue();
  loadPlateFromViewer(plate, acquisition, well, site, channel);
}


function getLoadedPlate() {
  // return first (and only) plate
  return loaded_plates.getFirstPlate();
}

function apiListPlates() {

  document.getElementById("left-sidebar-spinner").style.visibility = "visible";

  let formData = new FormData(document.getElementById('query-form'));
  formData.append("hide-unpublished-cb", getSelectedHideUnpublishedValue() );

  fetch('/api/list-plates', {
    method: 'POST',
    body: formData
  })
    .then(function (response) {

      if (response.status === 200) {
        response.json().then(function (json) {

          console.log('data', json);
          console.log('hiding spinner');
          document.getElementById("left-sidebar-spinner").style.visibility = "hidden";
          listPlatesQueryResultLoaded(json);

        });
      }
      else {
        response.text().then(function (text) {
          displayModalServerError(response.status, text);
        });
      }
    })
    .catch(function (error) {
      console.log(error);
      displayModalError(error);
    });
}

function listPlatesQueryResultLoaded(data) {
  let queryResults = data.results;
  drawPlatesListSidebar(queryResults);
}

function drawPlatesListSidebar(queryResults) {

  let list = document.getElementById('result-list');

  // Clear menu
  removeChildren(list);

  let last_proj = "";
  let plate_list = null;
  // Create sidebar as nested lists from query result
  queryResults.forEach(result => {

    // Create a list with all projects
    let proj = result.project;
    let plate_barcode = result.plate_barcode;
    let acq_name = result.acq_name;
    let acq_id = result.acq_id;

    // create a new sublist for each project
    if (last_proj !== proj) {
      let proj_item = document.createElement('li');
      proj_item.innerHTML = "<span style='cursor: pointer;''>" + proj + "</span>";
      list.appendChild(proj_item);
      plate_list = document.createElement('ul');
      proj_item.appendChild(plate_list);
    }

    // Create a list item for the plate
    let plate_item = document.createElement('li');
    let link = document.createElement('a');
    let linktext = acq_name;
    link.className = "text-info";
    link.href = "";

    link.setAttribute("data-toggle", "tooltip");
    link.setAttribute("data-placement", "top"); // Placement has to be off element otherwise flicker
    link.setAttribute("data-delay", "0");
    link.setAttribute("data-animation", false);
    link.title = linktext;

    let content = document.createTextNode(linktext);
    link.appendChild(content);
    plate_item.appendChild(link);

    // Add plate click handler
    plate_item.onclick = function (e) {
      e.preventDefault();
      apiLoadPlate(plate_barcode, acq_id);
    };

    // add plate item to projects plate_list
    plate_list.appendChild(plate_item);
    last_proj = proj;
  });

  //
  // Turn sidebar list into a clickable tree-view with projects collapsedm   vb
  // with this jQuery plugin
  //
  $('#result-list').bonsai({
    expandAll: false, // expand all items
    expand: null, // optional function to expand an item
    collapse: null, // optional function to collapse an item
    addExpandAll: false, // add a link to expand all items
    addSelectAll: false, // add a link to select all checkboxes
    selectAllExclude: null, // a filter selector or function for selectAll
    createInputs: false,
    checkboxes: false, // run quit(this.options) on the root node (requires jquery.qubit)
    handleDuplicateCheckboxes: false //update any other checkboxes that have the same value
  });

  // Tweak to get clickable project-names instead of only the little arrow
  // the project names are enclosed in <span></span>
  // https://github.com/aexmachina/jquery-bonsai/issues/23
  $('#result-list').on('click', 'span', function () {
    $(this).closest('li').find('> .thumb').click();
  });

  // Activate tooltips (all that have tooltip attribute within the resultlist)
  $('#result-list [data-toggle="tooltip"]').tooltip({
    trigger: 'hover',
    boundary: 'window'
  });

}

function apiLoadPlateBarcode(barcode) {
  console.log("Inside apiLoadPlateBarcode: ", barcode);
  apiLoadPlate(barcode);
}


function apiLoadPlate(plate_name, select_acq_id=undefined) {

  // stop any current animation
  stopAnimation();
  document.getElementById("animate-cbx").checked = false;

  url = '/api/plate/' + plate_name;
  fetch(url)
    .then(function (response) {
      if (response.status === 200) {

        //window.history.pushState('', '', url);

        response.json().then(function (json) {

          console.log('plate data', json);
          window.loaded_plates = new Plates(json['data'].plates);
          console.log(window.loaded_plates);
          console.log("Plates loaded")

          updateToolbarWithNewPlate(select_acq_id);

          redrawPlate(true);
        });
      }
      else {
        response.text().then(function (text) {
          displayModalServerError(response.status, text);
        });
      }
    })

    .catch(function (error) {
      console.log(error);
      displayModalError(error);
    });
}

function loadPlateFromViewer(plate_name, acquisition, well, site, channel) {

  // stop any current animation
  stopAnimation();
  document.getElementById("animate-cbx").checked = false;

  fetch('/api/plate/' + plate_name)

    .then(function (response) {
      if (response.status === 200) {
        response.json().then(function (json) {

          window.loaded_plates = new Plates(json['data'].plates);

          console.log(window.loaded_plates);

          updateToolbarWithNewPlate(acquisition, well, site, channel);

          console.log("done loadPlateFromViewer respone OK");

          redrawImageViewer();

        });
      }
      else {
        response.text().then(function (text) {
          displayModalServerError(response.status, text);
        });
      }

    })
    .catch(function (error) {
      console.log(error);
      displayModalError(error);
    });

}

function updateToolbarWithNewAcquisition() {

  updateWellSelect(getLoadedPlate());
  updateSiteSelect(getLoadedPlate());
  updateChannelSelect(getLoadedPlate());

}


function updateToolbarWithNewPlate(selected_acq_id, selected_well, selected_site, selected_channel){

  console.log("selected_well", selected_well);

  updateAcquisitionSelect(getLoadedPlate(), selected_acq_id);
  updateAcquisitionSlider(getLoadedPlate(selected_acq_id));

  updateWellSelect(getLoadedPlate(), selected_well);

  updateSiteSelect(getLoadedPlate(), selected_site);

  updateChannelSelect(getLoadedPlate(), selected_channel);

  updatePlateNameLabel(getLoadedPlate().getName());
  // updatePlateAcqLabel(getLoadedPlate());

  // Enable Animate checkbox
  if (getLoadedPlate().countAcquisitions() > 1) {
    document.getElementById("animate-cbx").disabled = false;
  }
}


function redrawPlateAndViewer(clearFirst = false) {

  if (document.getElementById('viewer-div')) {
    redrawImageViewer(clearFirst);
  }
  if (document.getElementById('plate-div')) {
    redrawPlate(clearFirst);
  }
}


function redrawImageViewer(clearFirst = true) {

  console.log("inside redrawImageViewer, clear first=", clearFirst);

  // get what to redraw

  let acquisition = getSelectedAcquisition();
  console.log("acquisition", acquisition);

  // Image viewer hack since it only takes a single site
  let site = getSelectedSite()[0];
  console.log("site", site);
  let well_name = getSelectedWell();
  console.log("well_name", well_name);
  let channels = getLoadedPlate().getChannels(acquisition, well_name, site);
  console.log("channels", channels);
  let imgURL = createMergeImgURLFromChannels(channels);

  console.log("imgUrl", imgURL);

  // Set brightness
  let brightness = getSelectedBrightnessValue();
  // This Openseadragon Brightness is working like css if I use the Coontrast filter instead
  let contrast = brightness / 100;
  viewer.setFilterOptions({
    filters: {
      processors: OpenSeadragon.Filters.CONTRAST(contrast)
    },
  });

  addImageToViewer(0, imgURL, 1);

  console.log('done redrawImageViewer');

}

function addImageToViewer(index, imgURL, opacity) {
  console.log('index', index);
  viewer.addSimpleImage({
    opacity: opacity,
    preload: true,
    type: 'image',
    url: imgURL,
    buildPyramid: false,
    sequenceMode: true,
    success: function (event) {
      console.log("image-loaded: n=" + index);
      console.log("item", event.item);
      console.log("source", event.item.source);
    }
  });
}


function redrawImageViewer_anime_version(clearFirst = true) {

  console.log("inside redrawImageViewer, clear first=", clearFirst)

  //clearFirst = true;

  if (clearFirst) {
    viewer.world.removeAll();
  }

  // get what to redraw
  let acquisitionIndex = getSelectedAcquisitionIndex();
  let acquisition = getSelectedAcquisition();
  console.log("acquisition", acquisition);

  // Image viewer hack since it only takes a single site
  let site = getSelectedSite()[0];

  console.log("site", site);
  let well_name = getSelectedWell();
  console.log("well_name", well_name);
  console.log("getLoadedPlate()", getLoadedPlate());
  let channels = getLoadedPlate().getChannels(acquisition, well_name, site);
  let imgURL = createMergeImgURLFromChannels(channels);

  // Set brightness
  let brightness = getSelectedBrightnessValue();
  // This Openseadragon Brightness is working like css if I use the Coontrast filter instead
  let contrast = brightness / 100;
  viewer.setFilterOptions({
    filters: {
      processors: OpenSeadragon.Filters.CONTRAST(contrast)
    },
  });

  console.log(" viewer.world.getItemCount()" + viewer.world.getItemCount());

  if (clearFirst) {
    // First load the selected acquisition
    //addImageToViewer(1, imgURL, 1);
    addImageToViewer(acquisitionIndex, imgURL, 1);

    // Then add the other ones
    loadAcquisitionImagesIntoViewer(acquisitionIndex);
  }

  // Now set opacity=1 on the image with the acquisition we want to see
  // set opacity = 0 on the rest
  console.log(" viewer.world.getItemCount()" + viewer.world.getItemCount());

  let tpCount = getLoadedPlate().countAcquisitions();
  for (let n = 0; n <= tpCount; n++) {
    let imgItem = viewer.world.getItemAt(n);
    console.log("n=" + n, imgItem);
  //  console.log(imgItem.source.url);
    if (imgItem) {
      if (n === acquisitionIndex) {
        imgItem.setOpacity(1);
      } else {
        imgItem.setOpacity(0);
      }
    }
  }
}

function loadAcquisitionImagesIntoViewer(skipIndex) {

  // get what to redraw
  let well_name = getSelectedWell();
  let tpCount = getLoadedPlate().countAcquisitions();

  // Image viewer hack since it only takes a single site
  let site = getSelectedSite()[0];


  // First odd ones
  for (let acquisitionIndex = 0; acquisitionIndex < tpCount; acquisitionIndex = acquisitionIndex + 1) {

    console.log("acquisitionIndex", acquisitionIndex);
    console.log("well_name", well_name);
    console.log("getLoadedPlate()", getLoadedPlate());

    let acquisitionID = getAcquisitionFromIndex(acquisitionIndex);
    let channels = getLoadedPlate().getChannels(acquisitionID, well_name, site);
    let imgURL = createMergeImgURLFromChannels(channels);

    if (acquisitionIndex !== skipIndex) {
      addImageToViewer(acquisitionIndex, imgURL, 0);
    }
  }
}



function openViewer(well_name, site_name) {

  let acquisition = getSelectedAcquisition();
  // let site = getSelectedSiteIndex();
  let channels = getLoadedPlate().getChannels(acquisition, well_name, site_name);
  let imgURL = createMergeImgURLFromChannels(channels);

  let viewerURL = "/image-viewer/" + getLoadedPlate().getName() +
    "/tp/" + acquisition +
    "/well/" + well_name +
    "/site/" + site_name +
    "/ch/" + getSelectedChannelValue() +
    "/url/" + imgURL;

  //window.open(viewerURL, "ImageViewerWindow");
  window.open(viewerURL);

}

// Redraws currently
function redrawPlate(clearFirst = false) {
  // get plate to draw
  let plateObj = getLoadedPlate();

  // get acquisition to draw
  let acquisition = getSelectedAcquisition();

  // get site to draw
  let site = getSelectedSite();

  drawPlate(plateObj, acquisition, site, clearFirst);

  drawImageAnalysisTableFiltered(plateObj)
}

function drawImageAnalysisTableFiltered(plateObj) {
  plate_barcode = plateObj.getName();
  apiCreateImageAnalysesTable(plate_barcode)
}

function createEmptyTable(rows, cols, sites) {
  let table = document.createElement('table');
  table.id = 'plateTable';
  table.className = 'plateTable';

  // First add header row
  let headerRow = document.createElement('tr');
  for (let col = 1; col <= cols; col++) {
    // If first col then add empty cell before (to match column headers)
    if (col === 1) {
      let empty_cell = document.createElement('td');
      empty_cell.innerHTML = "";
      empty_cell.className = 'headerCell';
      headerRow.appendChild(empty_cell);
    }
    let row = 0;
    let well_name = getWellName(row, col);
    let header_cell = document.createElement('td');
    header_cell.innerHTML = well_name.substring(1);
    header_cell.className = 'headerCell';
    headerRow.appendChild(header_cell);
  }
  table.appendChild(headerRow);

  // Now add rows and columns
  for (let row = 0; row < rows; row++) {
    let rowElement = document.createElement('tr');
    for (let col = 1; col <= cols; col++) {

      let well_name = getWellName(row, col);

      // Add column header before first column cell
      if (col === 1) {
        let header_cell = document.createElement('td');
        header_cell.innerHTML = well_name.charAt(0);
        header_cell.className = 'headerCell';
        rowElement.appendChild(header_cell);
      }

      let well_cell = document.createElement('td');
      well_cell.id = well_name;
      well_cell.className = 'wellCell';
      rowElement.appendChild(well_cell);

      let sites_table = create_site_layout(well_name, sites);

      well_cell.appendChild(sites_table);

    }
    table.appendChild(rowElement);
  }

  return table;
}

function create_site_layout(well_name, sites){

  let table = document.createElement('table');
  table.id = 'siteTable';
  table.className = 'siteTable';

  // Now add rows and columns
  nSites = sites.length;
  console.log("nSites", nSites);


  nRows = Math.ceil(Math.sqrt(nSites));
  nCols = Math.ceil(Math.sqrt(nSites));

  for (let row = 0; row < nRows; row++) {
    let rowElement = document.createElement('tr');
    //rowElement.className = 'siteRow';
    for (let col = 0; col < nCols; col++) {

      nSite = col + row * nCols // This if you want column order: nSite = row + col * nCols

      //console.log("add site: " + nSite);

      let site_name = sites[nSite];
      let cell_name = well_name + "_s" + site_name;

      let site_cell = document.createElement('td');
      site_cell.id = cell_name;
      site_cell.className = 'siteCell';
      rowElement.appendChild(site_cell);
    }
    table.appendChild(rowElement);

  }
  return table;

}


function createEmptyTable_old(rows, cols) {
  let table = document.createElement('table');
  table.id = 'plateTable';
  table.className = 'plateTable';

  // First add header row
  let headerRow = document.createElement('tr');
  for (let col = 1; col <= cols; col++) {
    // If first col then add empty cell before (to match column headers)
    if (col === 1) {
      let empty_cell = document.createElement('td');
      empty_cell.innerHTML = "";
      empty_cell.className = 'headerCell';
      headerRow.appendChild(empty_cell);
    }
    let row = 0;
    let well_name = getWellName(row, col);
    let header_cell = document.createElement('td');
    header_cell.innerHTML = well_name.substring(1);
    header_cell.className = 'headerCell';
    headerRow.appendChild(header_cell);
  }
  table.appendChild(headerRow);

  // Now add rows and columns
  for (let row = 0; row < rows; row++) {
    let rowElement = document.createElement('tr');
    for (let col = 1; col <= cols; col++) {

      let well_name = getWellName(row, col);

      // Add column header before first column cell
      if (col === 1) {
        let header_cell = document.createElement('td');
        header_cell.innerHTML = well_name.charAt(0);
        header_cell.className = 'headerCell';
        rowElement.appendChild(header_cell);
      }

      let well_cell = document.createElement('td');
      well_cell.id = well_name;
      well_cell.className = 'wellCell';
      rowElement.appendChild(well_cell);
    }
    table.appendChild(rowElement);
  }

  return table;
}

function drawPlate(plateObj, acquisition, sites, clearFirst) {

  console.log("plateObj", plateObj);
  console.log("clearFirst", clearFirst);

  let container = document.getElementById('plate-div');

  // If for example a new plate have been selected
  // all old well_images should be removed since plate layout might change
  // But will not get cleared first if it is an animation

  // TODO change this hack for smoother animation
  clearFirst = true;
  if (clearFirst) {
    removeChildren(container);
  }

  let siteNames = sites; // plateObj.getAvailableSites();

  // first create a new plate consisting of empty well-div's
  if (document.getElementById('plateTable') == null) {
    let plateLayout = plateObj.getPlateSize(siteNames);
    let table = createEmptyTable(plateLayout.rows, plateLayout.cols, plateLayout.sites);
    container.appendChild(table);
    console.log('done create div');
  }

  console.log(container);

  console.log("acquisition", acquisition);

  // now populate well-div's with the wells of the plateobj
  let wells = plateObj.getWells(acquisition);
  Object.keys(wells).forEach(well_key => {
    let well = wells[well_key];

    // Add the sites that are selected to be shown
    let nSites = siteNames.length;
    for(let nSite = 0; nSite < nSites; nSite++) {

      let site_name = siteNames[nSite];

      let site = well.sites[site_name];
      if(site != null){

        console.log("site", site);

        let site_key = well_key + "_s" + site_name;
        console.log("site_key", site_key);
        let site_cell = document.getElementById(site_key);

        console.log("siteNames", siteNames);
        console.log("site_name", site_name);
        console.log("well_key", well_key);

        // Try to get existing canvas - if it doesn't exist create it
        // this way we are only drawing images on top of existing images
        // and animation becomes smooth
        let siteCanvas = document.getElementById('siteCanvas' + site_key);
        if (siteCanvas == null) {

          siteCanvas = document.createElement('canvas');
          siteCanvas.className = 'siteCanvas';
          siteCanvas.id = 'siteCanvas' + site_key;

          // TODO fix resizing of canvas
          // Canvas size should not be set with css-style
          siteCanvas.width = 100;
          siteCanvas.height = 100;
          //siteCanvas.style.border = "2px solid #ffff00";

          site_cell.appendChild(siteCanvas);
        }
        let zoom = getSelectedZoomValue();
        let scale = zoom / 100;

        siteCanvas.width = 100 * scale;
        siteCanvas.height = 100 * scale;

        let context = siteCanvas.getContext('2d');



        if(site.channels != null){

          let url = createMergeThumbImgURLFromChannels(site.channels);
          let img = document.createElement('img');
          img.src = url;
          img.className = 'cellThumbImg';
          img.id = 'cellThumbImg' + site_key;

          // Get filter values
          let brightness = getSelectedBrightnessValue() / 100;

          //wellThumbImg
          img.onload = function () {
            context.filter = 'brightness(' + brightness + ')'
            context.drawImage(img, 0, 0);
          };

          // Create open Viewer click handlers
          siteCanvas.onclick = function () {
            openViewer(well_key, site_name);
          }

        }

        // Add tooltip when hoovering an image
        // siteCanvas.setAttribute("data-toggle", "tooltip");
        // siteCanvas.setAttribute("data-placement", "right"); // Placement has to be off element otherwise flicker
        // siteCanvas.setAttribute("data-delay", "0");
        // siteCanvas.setAttribute("data-animation", false);
        // siteCanvas.setAttribute("data-html", true);
        siteCanvas.title = site_key; //plateObj.getFormattedWellMeta(acquisition, well_key);
      }

    }

  })

  // Activate tooltips (all that have tooltip attribute within the resultlist)
  // Not working because tooltip doesn't get updated
  // $('#plate-div [data-toggle="tooltip"]').tooltip({
  //   trigger : 'hover',
  //   boundary: 'window',
  //   // onBeforeShow: getWellMeta()
  // });

}

function getSelectedAcquisitionIndex() {
  let elem = document.getElementById('acquisition-select');
  return elem.selectedIndex;
}

function getSelectedAcquisitionId() {
  let elem = document.getElementById('acquisition-select');
  return getAcquisitionFromIndex(elem.selectedIndex);
}

function getAcquisitionFromIndex(index) {
  let elem = document.getElementById('acquisition-select');
  return elem.options[index].value;
}

function getSelectedAcquisition() {
  let elem = document.getElementById('acquisition-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedZoomValue() {
  let elem = document.getElementById('zoom-select');
  return parseInt(elem.options[elem.selectedIndex].value);
}

function getSelectedBrightnessValue() {
  let elem = document.getElementById('brightness-select');
  return parseInt(elem.options[elem.selectedIndex].value);
}

function getSelectedHideUnpublishedValue() {
  return document.getElementById('hide-unpublished-cb').checked;
}

function selectBrightnessFromStoredValue(){
  let brightness = getBrightnessFromStore();
  console.log("brightness", brightness);
  let elem = document.getElementById('brightness-select');
  let index = getIndexFromValue(elem.options, brightness);
  elem.selectedIndex = index;
}

function selectHideUnpublishedFromStoredValue(){
  let hideUnpublished = getHideUnpublishedFromStore();
  console.log("hideUnpublished", hideUnpublished);
  document.getElementById('hide-unpublished-cb').checked = hideUnpublished;
}

function setSelectedAcquisition(acquisitionID) {

  console.log("acquisitionID", acquisitionID);

  let elem = document.getElementById('acquisition-select');
  let index = getIndexFromValue(elem.options, acquisitionID);

  setSelectedAcquisitionByIndex(index);

}

function setSelectedAcquisitionByIndex(index) {
  let elem = document.getElementById('acquisition-select');

  elem.selectedIndex = index;
  console.log("index", index);
  // elem.options[elem.selectedIndex].value = index;
  updateAcquisitionSliderPos();
  redrawPlateAndViewer();

}

function getIndexFromValue(options, value) {
  console.log("options", options);

  for (i = 0; i < options.length; i++) {
    console.log(options[i].value);

    if (options[i].value == value) {
      console.log("value", value);
      return i;
    }
  }

  return 0;

}

function getSelectedChannelValue() {
  let elem = document.getElementById('channel-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedSiteIndex() {
  let elem = document.getElementById('site-select');
  return parseInt(elem.options[elem.selectedIndex].value);
}

function getSelectedSite() {
  let elem = document.getElementById('site-select');
  return JSON.parse(elem.options[elem.selectedIndex].value);
}

function getSelectedWell() {
  let elem = document.getElementById('well-select');
  return elem.options[elem.selectedIndex].value;
}

function getSelectedAnimationSpeed() {
  let elem = document.getElementById('animation-speed-select');
  return parseInt(elem.options[elem.selectedIndex].value);
}


function updateAcquisitionSelect(plateObj, selected_acq_id=undefined) {
  let elemSelect = document.getElementById('acquisition-select');

  // reset
  elemSelect.options.length = 0;

  // add as many options as acquisitions
  let acquisitions = plateObj.getAcquisitions();
  let nCount = Object.keys(acquisitions).length;
  for (let n = 0; n < nCount; n++) {

    plate_acq_id = Object.keys(acquisitions)[n];

    selected = (selected_acq_id == plate_acq_id) ? true : false;

    elemSelect.options[n] = new Option(plate_acq_id, plate_acq_id, selected, selected);

  }

  // Enable or disable if there is more than one option
  if (elemSelect.options.length <= 1) {
    elemSelect.disabled = true;
    console.log("elemSelect.disabled", elemSelect.disabled);
  }
  else {
    elemSelect.disabled = false;
  }

}

function updateAcquisitionSliderPos() {
  let nSelected = getSelectedAcquisitionIndex();

  // update
  let slider = $("#acquisition-slider").data("ionRangeSlider");
  slider.update({
    from: nSelected
  });
}


function updateAcquisitionSlider(plateObj) {
  let nCount = plateObj.countAcquisitions();

  // Always disable for now
  disable = true;

  //// disable if single acquisition
  //let disable = true;
  //if (nCount > 0) {
  //  disable = false;
  //}

  // Get slider function
  let slider = $("#acquisition-slider").data("ionRangeSlider");

  let nSelected = getSelectedAcquisitionIndex();

  // update
  slider.update({
    from: nSelected,
    min: 0,
    max: nCount - 1,
    disable: disable
  });
}

function toggleAnimation() {
  if (document.getElementById("animate-cbx").checked) {
    // Check that animation is not ongoing already
    if (window.animation == null) {
      startAnimation();
    }
  } else {
    stopAnimation();
  }
}

function updateShowScalebar() {

  // Default 0 pixPerMeter which means scalebar will be hidden
  let pixPerMeter = 0;
  if (document.getElementById("scalebar-cbx").checked) {

    // TODO get actual pix per meter for current image
    pixPerMeter = 1000000;
  }

  let scalebarOptions = {};
  scalebarOptions["pixelsPerMeter"] = pixPerMeter;
  viewer.scalebar(scalebarOptions);
}


function stopAnimation() {
  if (window.animation) {
    clearInterval(window.animation);
    window.animation = null;
  }
}

function startAnimation() {
  let speed = getSelectedAnimationSpeed();
  let delay = 1000 - (speed * 100);
  let nAcquisitions = getLoadedPlate().countAcquisitions();

  window.animation = setInterval(function () {
    let current = getSelectedAcquisitionIndex();
    let next = current + 1;
    if (next >= nAcquisitions) {
      next = 0;
    }
    console.log("next", next);
    setSelectedAcquisitionByIndex(next);

  }, delay);
}

/*
* Update animation speed by restarting animation
*/
function updateAnimationSpeed() {
  // Only update if running
  if (window.animation) {
    stopAnimation();
    startAnimation();
  }
}


function updateWellSelect(plateObj, selected_well) {

  // This select is not available on all pages, return if not
  let elemSelect = document.getElementById('well-select');
  if (elemSelect == null) {
    return;
  }

  // reset
  elemSelect.options.length = 0;

  let wells = plateObj.getWells(getSelectedAcquisitionId());
  Object.keys(wells).forEach(function (well_key) {
    selected = (selected_well == well_key) ? true : false;
    elemSelect.options.add(new Option(well_key, well_key, selected, selected));
  });

  console.log("elemSelect.", elemSelect.selectedIndex);

}

function setWellSelection(well) {
  let elemSelect = document.getElementById('well-select');
  elemSelect.selectedIndex = getSelectIndexFromSelectValue(elemSelect, well);
}

function setSiteSelection(site) {
  let elemSelect = document.getElementById('site-select');
  elemSelect.selectedIndex = getSelectIndexFromSelectValue(elemSelect, site);
}

function setChannelSelection(channel) {
  let elemSelect = document.getElementById('channel-select');
  elemSelect.selectedIndex = getSelectIndexFromSelectValue(elemSelect, channel);
}


function getSelectIndexFromSelectValue(elemSelect, value) {
  let index = -1;
  for (let i = 0; i < elemSelect.length; i++) {
    if (value === elemSelect.options[i].value) {
      index = i;
      break;
    }
  }
  return index;
}

function updateSiteSelect(plateObj, selected_site) {
  let elemSelect = document.getElementById('site-select');

  // reset
  elemSelect.options.length = 0;

  // add as many options as sites
  let siteNames = plateObj.getAvailableSites(getSelectedAcquisitionId());

  // Loop through the siteNames array
  for (let name of siteNames) {
    option_json = "[" + name + "]";
    selected = (selected_site == option_json) ? true : false;
    elemSelect.add(new Option(option_json, option_json, selected, selected));
  }

  // finally add an "all" option
  let allOption = JSON.stringify(siteNames)
  elemSelect.add(new Option(allOption, allOption));



}

function updatePlateNameLabel(plate_name) {
  document.getElementById('plate-name-label').innerHTML = "Plate: " + plate_name;
  document.getElementById('plate-name-label').title = "Plate: " + plate_name;
}

function updatePlateAcqLabel(plateObj) {

  let plate_acq_id = getSelectedAcquisitionId()

  document.getElementById('plate-acq-label').innerHTML = "Acq-id: " + plate_acq_id;
  document.getElementById('plate-acq-label').title = "Acq-id: " + plate_acq_id;
}

function updateChannelSelect(plateObj, selected_channel) {
  let elemSelect = document.getElementById('channel-select');

  // reset
  elemSelect.options.length = 0;

  let nCount = plateObj.countChannels(getSelectedAcquisitionId());

  console.log("channelcount", nCount);

  // First add default (Merge channels options)
  if (nCount === 1) {
    elemSelect.options[0] = new Option("1", "1");
  } else if (nCount === 2) {
    elemSelect.options[0] = new Option("1-2");
  } else if (nCount >= 3) {
    elemSelect.options[0] = new Option("1-3");
  }

  // add as many options as channels
  let channel_names = plateObj.getChannelNames(getSelectedAcquisitionId());
  for (let n = 1; n <= nCount; n++) {
    channel_name = channel_names[n - 1];
    channel_option_text = "" + n + "-" + channel_name
    selected = (selected_channel == channel_name) ? true : false
    elemSelect.add(new Option(channel_option_text, n, selected, selected));
  }
}

function removeChildren(domObject) {
  while (domObject.firstChild) {
    domObject.removeChild(domObject.firstChild);
  }
}

function createMergeThumbImgURLFromChannels(channels) {

  let selected_channel = String(getSelectedChannelValue());

  let url = null;
  if (selected_channel === '1-2') {
    let key_ch1 = Object.keys(channels)[0];
    let key_ch2 = Object.keys(channels)[1];
    url = "/api/image-merge-thumb/ch1/" + channels[key_ch1].path + "/ch2/" + channels[key_ch2].path + "/ch3/" + 'undefined' + "/channels.png";
  } else if (selected_channel === '1-3') {
    let key_ch1 = Object.keys(channels)[0];
    let key_ch2 = Object.keys(channels)[1];
    let key_ch3 = Object.keys(channels)[2];
    url = "/api/image-merge-thumb/ch1/" + channels[key_ch1].path + "/ch2/" + channels[key_ch2].path + "/ch3/" + channels[key_ch3].path + "/channels.png";
  } else {
    let channelIndex = parseInt(selected_channel, 10) - 1;
    let key_chx = Object.keys(channels)[channelIndex];
    url = "/api/image-merge-thumb/ch1/" + channels[key_chx].path + "/ch2/" + 'undefined' + "/ch3/" + 'undefined' + "/channels.png"
  }

  return url;
}

function createMergeImgURLFromChannels(channels) {

  console.log(channels, channels);
  if(!channels){
    return "/static/images/empty.png";
  }

  let selected_channel = String(getSelectedChannelValue());

  let url = null;
  if (selected_channel === '1-2') {
    let key_ch1 = Object.keys(channels)[0];
    let key_ch2 = Object.keys(channels)[1];
    url = "/api/image-merge/ch1/" + channels[key_ch1].path + "/ch2/" + channels[key_ch2].path + "/ch3/" + 'undefined' + "/channels.png";
  } else if (selected_channel === '1-3') {
    let key_ch1 = Object.keys(channels)[0];
    let key_ch2 = Object.keys(channels)[1];
    let key_ch3 = Object.keys(channels)[2];
    url = "/api/image-merge/ch1/" + channels[key_ch1].path + "/ch2/" + channels[key_ch2].path + "/ch3/" + channels[key_ch3].path + "/channels.png";
  } else {
    let channelIndex = parseInt(selected_channel, 10) - 1;
    let key_chx = Object.keys(channels)[channelIndex];
    url = "/api/image-merge/ch1/" + channels[key_chx].path + "/ch2/" + 'undefined' + "/ch3/" + 'undefined' + "/channels.png"
  }

  return url;
}

function getWellName(row, col) {
  let rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P","Q","R","S","T","U","V","W","X","Y","Z","[","\\","]","^","_","`","a","b"]
  return rows[row] + col.toString().padStart(2, 0)
}

function getRowIndexFrowWellName(name) {
  let ascVal = name.charCodeAt(0);
  // A = char code 65
  let rowIndex = ascVal - 64;
  return rowIndex;
}

function getColIndexFrowWellName(name) {
  let colIndex = parseInt(name.substr(1), 10);
  return colIndex;
}

function displayModalServerError(status, text) {
  displayModalError("Server error: " + status + ", Response: " + text);
}

function displayModalJavaScriptError(message, source, lineno, colno, error) {
  console.log(error);
  displayModalError("Javascript error:<br>" + message + "<br>" + error.stack);
}

function displayModalError(text) {
  document.getElementById('errordiv').innerHTML = "<pre>" + text + "</pre>";
  console.log("text", text);
  $("#error-modal").modal();
}

/*
*
* Tool event handlers
*
*/
function zoomSelectChanged() {
  redrawPlate();
}

function brightnessSelectChanged() {
  let brightness = getSelectedBrightnessValue();
  setBrightnessInStore(brightness);
  redrawPlate();
}

function hideUnpublishedSelectChanged() {
  let hideUnpublished = getSelectedHideUnpublishedValue();
  setHideUnpublishedInStore(hideUnpublished);
  location.reload();
}

function acquisitionSelectChanged() {
  updateToolbarWithNewAcquisition();
  redrawPlate();
}

function siteSelectChanged() {
  redrawPlate();
}

function channelSelectChanged() {
  redrawPlate();
}

function animationSpeedSelectChanged() {
  updateAnimationSpeed();
}

function animateCbxChanged() {
  toggleAnimation();
}

function viewerBrightnessSelectChanged() {
  redrawImageViewer();
}

function viewerAcquisitionSelectChanged() {
  redrawImageViewer(false);
}

function viewerSiteSelectChanged() {
  redrawImageViewer();
}

function viewerChannelSelectChanged() {
  redrawImageViewer();
}

function viewerWellSelectChanged() {
  redrawImageViewer();
}

function viewerAnimationSpeedSelectChanged() {
  updateAnimationSpeed();
}

function viewerAnimateCbxChanged() {
  toggleAnimation();
}

function viewerScalebarCbxChanged() {
  updateShowScalebar();
}


/*
  Code from pipelinegui
*/

function apiCreateImageAnalysesTable(plate_barcode) {

  let limit = 1000;
  let sortOrder = "ASCENDING"
  // let plate_barcode = ""
  let plate_acq_id = ""

  fetch('/api/list/image_analyses/' + limit + "/" + sortOrder + "/" + plate_barcode)

    .then(function (response) {
      if (response.status === 200) {
        response.json().then(function (json) {

          console.log('result', json);
          drawImageAnalysisTable(json['result']);

        });
      }
      else {
        response.text().then(function (text) {
          displayModalServerError(response.status, text);
        });
      }
    })

    .catch(function (error) {
      console.log(error);
      displayModalError(error);
    });

}

function drawImageAnalysisTable(rows) {


  // Before drawing table add ("View in notebook")
  rows = addNotebookLinkColumn(rows)

  // Before drawing table add ("File-Links")
  rows = addFileLinksColumn(rows)

  // Truncate "result" column
  rows = truncateColumn(rows, "result", 100);

  drawTable(rows, "image_analyses-table-div");

}

function addNotebookLinkColumn(rows) {

  console.log("Inside Add NotebokLinkColumn");

  // Define which column in result contains the id
  let result_col_index = 9;

  // Add new column header to end of header row
  let cols = rows[0];
  cols.push("Jupyter Link")

  let name_col_index = 0;
  let base_url = "https://cpp-notebook-nogpu.k8s-prod.pharmb.io" + "/lab/tree" + "/mnt/cpp-pvc/";

  // Start from row 1 (0 is headers)
  for (let nRow = 1; nRow < rows.length; nRow++) {

    let result = rows[nRow][result_col_index];
    console.log("result_list", result);

    let cell_contents = "";

    if (result && result.job_folder) {

      let link_url = base_url + result.job_folder


      // results/384-P000014-helgi-U2OS-24h-L1-copy2/60/15

      cell_contents = "<a target='notebook' href='" + link_url + "'>Link</a>"

    }

    rows[nRow].push(cell_contents);

  }

  return rows;

}

function addFileLinksColumn(rows) {
  console.log("Inside addFileLinksColumn");

  BASE_URL = window.PIPELINEGUI_URL + "/";

  // Add header to new cell
  let cols = rows[0];
  result_col_index = cols.indexOf("result");

  cols.splice(result_col_index + 1, 0, "file_list-links");
  console.log("rows.length", rows.length);

  // Create new cell in all rows
  for (let nRow = 1; nRow < rows.length; nRow++) {

    console.log("nRow:", nRow);

    let result = rows[nRow][result_col_index];
    console.log("result:)", result);

    let cell_contents = "";

    if (result != null) {
      console.log("result.file_list", result.file_list);
      for (var file_path of result.file_list) {
        console.log("file_path", file_path);
        if (file_path.endsWith(".pdf") || file_path.endsWith(".csv")) {
          console.log("file_path", file_path);

          link_text = basename(file_path);

          let linkified_file_path = "<a href='" + BASE_URL + file_path + "'>" + link_text + "</a>";
          cell_contents += linkified_file_path + ", "
        }
      }
    }

    // Add result column result with new result content
    rows[nRow].splice(result_col_index + 1, 0, cell_contents);

  }

  return rows;
}

function basename(str) {
  let separator = "/";
  return str.substr(str.lastIndexOf(separator) + 1);
}

function truncateColumn(rows, column_name, trunc_length) {
  let cols = rows[0];
  column_index = cols.indexOf(column_name);

  for (let nRow = 1; nRow < rows.length; nRow++) {
    console.log("nRow:", nRow);

    let content = rows[nRow][column_index];
    if (typeof content == 'object') {
      content = JSON.stringify(content);
    }

    if (content === "null") {
      content = "";
    }

    if (content != null && content.length > trunc_length) {
      content = content.substring(0, trunc_length);
      content += "....."
    }

    rows[nRow][column_index] = content;
  }

  return rows;

}

function drawTable(rows, divname) {

  console.log("rows", rows);
  console.log("divname", divname);

  let container = document.getElementById(divname);

  // Create Table
  let table = document.createElement('table');
  table.id = divname + "-table";
  table.className = 'table text-xsmall table-bordered';

  // First add header row
  let headerRow = document.createElement('tr');

  // First row in rows is headers
  let cols = rows[0];

  for (let col = 0; col < cols.length; col++) {

    let header_cell = document.createElement('th');
    header_cell.innerHTML = cols[col];
    //header_cell.className = 'headerCell';
    headerRow.appendChild(header_cell);
  }
  table.appendChild(headerRow);

  // Now add rows (start from 1 since 0 is headers)
  for (let row = 1; row < rows.length; row++) {
    let rowElement = document.createElement('tr');
    for (let col = 0; col < cols.length; col++) {

      let cell = document.createElement('td');
      let content = rows[row][col];
      if (typeof content == 'object') {
        content = JSON.stringify(content);
      }

      if (content === "null") {
        content = "";
      }

      cell.innerHTML = content;

      //cell.className = 'tableCell';
      rowElement.appendChild(cell);
    }

    table.appendChild(rowElement);
  }

  removeChildren(container);
  container.append(table)

  console.log("drawTable finished")

}

/*
*
*  Cookie-store section
*
*/
function getCookie(name) {
  let cookie = {};
  document.cookie.split(';').forEach(function (el) {
      let [k, v] = el.split('=');
      cookie[k.trim()] = v;
  });
  return cookie[name];
}

function setCookie(name, value, expires = "Tue, 19 Jan 2038 03:14:00 UTC") {
  let cookie_string = name + "=" + value + ";expires=" + expires + ";path=/";
  console.log("cookiestring", cookie_string);
  document.cookie = cookie_string;
}

function deleteCookie(name) {
  setCookie(name, '', "Thu, 01 Jan 1970 00:00:00 GMT");
}

function setCookieData(name, data) {
  console.log("data:", data);
  // Data is stored in base64 encoded and in json format
  let value = window.btoa(JSON.stringify(data));
  setCookie(name, value);
}

function getCookieData(name) {
  let cookie = getCookie(name);
  console.log("cookie", cookie);
  if (cookie == null) {
      return null;
  } else {
      // Data is base64 encoded and in json format
      return JSON.parse(window.atob(cookie));
  }
}

function getBrightnessFromStore() {
  let brightness = getCookieData("brightness");

  if (brightness == null) {
    brightness = getDefaultBrightness();
  }
  return brightness;
}

function getHideUnpublishedFromStore() {
  let hideUnpublished = getCookieData("hideUnpublished");

  if (hideUnpublished == null) {
    hideUnpublished = getDefaultHideUnpublished();
  }
  return hideUnpublished;
}

function getDefaultBrightness(){
  return 100;
}

function getDefaultHideUnpublished(){
  return true;
}

function setBrightnessInStore(brightness) {
  setCookieData("brightness", brightness);
}

function setHideUnpublishedInStore(hideUnpublished) {
  setCookieData("hideUnpublished", hideUnpublished);
}

