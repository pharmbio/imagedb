/*
  Javascript version: ECMAScript 6 (Javascript 6)
 */
  class Plate {
    constructor(jsonData) {
      this.data = jsonData;
    }

    getName() {
      return this.data.id;
    }

    getProjectName(acquisitionId) {
      return this.getAcquisitions()[acquisitionId]?.project || "None";
    }

    setProjectTrash(acquisitionId) {
      this.getAcquisitions()[acquisitionId].project="trash";
    }

    getAcquisitionFolder(acquisitionId) {
      return this.getAcquisitions()[acquisitionId]?.folder || "None";
    }

    getLayout() {
      return this.data.layout;
    }

    getWellLayoutMeta(wellName) {
      return this.getLayout()?.[wellName] || [];
    }

    getAcquisitions() {
      return this.data.acquisitions;
    }

    getWells(acquisitionId) {
      return this.getAcquisitions()[acquisitionId]?.wells || {};
    }

    getSites(acquisitionId, wellKey) {
      return this.getWells(acquisitionId)[wellKey]?.sites || {};
    }

    getZPositions(acquisitionId, wellKey, siteKey) {
      return this.getSites(acquisitionId, wellKey)[siteKey]?.z_positions || {};
    }

    getChannels(acquisitionId, wellKey, siteKey, zKey) {
      return this.getZPositions(acquisitionId, wellKey, siteKey)[zKey]?.channels || {};
    }

    getFirstWellKey(acquisitionId) {
      return Object.keys(this.getWells(acquisitionId))[0];
    }

    getFirstSiteKey(acquisitionId, wellKey) {
      return Object.keys(this.getSites(acquisitionId, wellKey))[0];
    }

    getFirstZPositionKey(acquisitionId, wellKey, siteKey) {
      return Object.keys(this.getZPositions(acquisitionId, wellKey, siteKey))[0];
    }
/*
    getSiteNames(acquisitionId) {
      const firstWellKey = this.getFirstWellKey(acquisitionId);
      const sites = this.getSites(acquisitionId, firstWellKey);
      return Object.values(sites).map(site => site.id);
    }
*/
    getSiteNames(acquisitionId) {
      const startTime = performance.now();

      const siteNamesSet = new Set();
      const wells = this.getWells(acquisitionId);
      for (const wellKey of Object.keys(wells)) {
        const sites = this.getSites(acquisitionId, wellKey);
        for (const site of Object.values(sites)) {
          siteNamesSet.add(site.id);
        }
      }

      // Convert set to array and sort numerically
      const sortedSiteNames = Array.from(siteNamesSet).sort((a, b) => Number(a) - Number(b));
      const elapsed = performance.now() - startTime;
      console.log(`Collecting and sorting unique site names took ${elapsed.toFixed(2)} ms`);

      return sortedSiteNames;
    }

    /*
    getChannelNames(acquisitionId) {
      const firstWellKey = this.getFirstWellKey(acquisitionId);
      const firstSiteKey = this.getFirstSiteKey(acquisitionId, firstWellKey);
      const firstZPositionKey = this.getFirstZPositionKey(acquisitionId, firstWellKey, firstSiteKey);
      const channels = this.getChannels(acquisitionId, firstWellKey, firstSiteKey, firstZPositionKey);
      return Object.values(channels).map(channel => channel.dye);
    }
    */

    getChannelNames(acquisitionId) {
      const startTime = performance.now();

      const channelNamesSet = new Set();
      const wells = this.getWells(acquisitionId);

      for (const wellKey of Object.keys(wells)) {
        const sites = this.getSites(acquisitionId, wellKey);
        for (const siteKey of Object.keys(sites)) {
          const zPositions = this.getZPositions(acquisitionId, wellKey, siteKey);
          for (const zKey of Object.keys(zPositions)) {
            const channels = this.getChannels(acquisitionId, wellKey, siteKey, zKey);
            for (const channel of Object.values(channels)) {
              channelNamesSet.add(channel.dye);
            }
          }
        }
      }

      console.log("channelNamesSet", channelNamesSet);

      // Convert the Set to an Array and sort numerically when possible.
      const sortedChannelNames = Array.from(channelNamesSet).sort((a, b) => {
        const numA = Number(a);
        const numB = Number(b);
        const isNumA = !isNaN(numA);
        const isNumB = !isNaN(numB);

        if (isNumA && isNumB) {
          return numA - numB;
        }
        return a.localeCompare(b);
      });

      console.log("sortedChannelNames", sortedChannelNames);

      const elapsed = performance.now() - startTime;
      console.log(`Collecting and sorting unique channel names took ${elapsed.toFixed(2)} ms`);

      return sortedChannelNames;
    }


    /*
    getAvailableChannels(acquisitionId) {
      const firstWellKey = this.getFirstWellKey(acquisitionId);
      const firstSiteKey = this.getFirstSiteKey(acquisitionId, firstWellKey);
      const firstZPositionKey = this.getFirstZPositionKey(acquisitionId, firstWellKey, firstSiteKey);
      return this.getChannels(acquisitionId, firstWellKey, firstSiteKey, firstZPositionKey);
    }
    */

    /*
    getAvailableChannels(acquisitionId) {
      const startTime = performance.now();

      const firstWellKey = this.getFirstWellKey(acquisitionId);
      const firstSiteKey = this.getFirstSiteKey(acquisitionId, firstWellKey);
      const firstZPositionKey = this.getFirstZPositionKey(acquisitionId, firstWellKey, firstSiteKey);
      const availableChannels = this.getChannels(acquisitionId, firstWellKey, firstSiteKey, firstZPositionKey);

      const elapsed = performance.now() - startTime;
      console.log(`Collecting available channels took ${elapsed.toFixed(2)} ms`);

      return availableChannels;
    }
      */

    getAvailableChannels(acquisitionId) {
      const startTime = performance.now();

      // We'll use a Map to ensure uniqueness.
      // The key will be a string composed of channel.id and channel.dye.
      const uniqueChannelsMap = new Map();
      const wells = this.getWells(acquisitionId);

      for (const wellKey of Object.keys(wells)) {
        const sites = this.getSites(acquisitionId, wellKey);
        for (const siteKey of Object.keys(sites)) {
          const zPositions = this.getZPositions(acquisitionId, wellKey, siteKey);
          for (const zKey of Object.keys(zPositions)) {
            const channels = this.getChannels(acquisitionId, wellKey, siteKey, zKey);
            for (const channel of Object.values(channels)) {
              // Create a unique key. Adjust this as needed.
              const key = `${channel.id}-${channel.dye}`;
              // If not already in the map, add it.
              if (!uniqueChannelsMap.has(key)) {
                // Save only the needed properties.
                uniqueChannelsMap.set(key, { id: channel.id, dye: channel.dye });
              }
            }
          }
        }
      }

      // Convert the map values to an array.
      // Here, we sort by channel.id numerically when possible,
      // otherwise we sort lexicographically.
      const uniqueChannels = Array.from(uniqueChannelsMap.values()).sort((a, b) => {
        const numA = Number(a.id);
        const numB = Number(b.id);
        const isNumA = !isNaN(numA);
        const isNumB = !isNaN(numB);
        if (isNumA && isNumB) {
          return numA - numB;
        }
        return a.id.localeCompare(b.id);
      });

      const elapsed = performance.now() - startTime;
      console.log(`Collecting and sorting unique channels took ${elapsed.toFixed(2)} ms`);

      console.log(`uniqueChannels`, uniqueChannels);

      return uniqueChannels;
    }


    /*
    getAvailableZpos(acquisitionId) {
      const firstWellKey = this.getFirstWellKey(acquisitionId);
      const firstSiteKey = this.getFirstSiteKey(acquisitionId, firstWellKey);
      return Object.keys(this.getZPositions(acquisitionId, firstWellKey, firstSiteKey));
    }*/

    getAvailableZpos(acquisitionId) {
        const startTime = performance.now();
        const zPosSet = new Set();
        const wells = this.getWells(acquisitionId);

        for (const wellKey of Object.keys(wells)) {
          const sites = this.getSites(acquisitionId, wellKey);
          for (const siteKey of Object.keys(sites)) {
            const zPositions = this.getZPositions(acquisitionId, wellKey, siteKey);
            for (const zKey of Object.keys(zPositions)) {
              zPosSet.add(zKey);
            }
          }
        }

        // Convert the set to an array and sort numerically.
        const sortedZPos = Array.from(zPosSet).sort((a, b) => Number(a) - Number(b));
        const elapsed = performance.now() - startTime;
        console.log(`Collecting unique Z positions took ${elapsed.toFixed(2)} ms`);
        return sortedZPos;
    }

    getPlateSize(siteNames) {
      // Loop through wellNames (for all acquisitions) and see if size is outside 96 or 384 plate limit
      // if not return 96, 384 or 1536
      let maxRow = 1;
      let maxCol = 1;
      for (let acquisitionId of Object.keys(this.getAcquisitions())) {
        let wells = this.getWells(acquisitionId);
        for (let wellKey of Object.keys(wells)) {
          let wellName = wells[wellKey].id;
          let nRow = Plate.getRowIndexFromWellName(wellName);
          let nCol = Plate.getColIndexFromWellName(wellName);
          maxRow = Math.max(maxRow, nRow);
          maxCol = Math.max(maxCol, nCol);
        }
      }

      if (maxRow > 32 || maxCol > 48) return { rows: maxRow, cols: maxCol, sites: siteNames }; // Custom size
      if (maxRow > 16 || maxCol > 24) return { rows: 32, cols: 48, sites: siteNames }; // 1535
      if (maxRow > 8 || maxCol > 12) return { rows: 16, cols: 24, sites: siteNames }; // 384
      return { rows: 8, cols: 12, sites: siteNames }; // 96
    }


      /**
       * Counts the number of acquisitions in the plate.
       * @returns {number} The count of acquisitions.
       */
    countAcquisitions() {
      return Object.keys(this.getAcquisitions()).length;
    }

      /**
       * Counts the number of channels for the first non-empty well and site
       * for the given acquisition ID. Returns 0 if no channels are found.
       *
       * @param {String} acquisitionId The acquisition ID to count channels for.
       * @returns {number} The count of channels.
       */
    countChannels(acquisitionId) {
      const firstWellKey = this.getFirstWellKey(acquisitionId);
      const firstSiteKey = this.getFirstSiteKey(acquisitionId, firstWellKey);
      const firstZPositionKey = this.getFirstZPositionKey(acquisitionId, firstWellKey, firstSiteKey);
      const channels = this.getChannels(acquisitionId, firstWellKey, firstSiteKey, firstZPositionKey);
      return Object.keys(channels).length;
    }

      /**
       * Counts the number of wells in the first acquisition. Assumes that the number of wells is consistent across acquisitions.
       * @returns {number} The count of wells in the first acquisition, or 0 if no acquisitions are present.
       */
    countWells() {
      const acquisitionIds = Object.keys(this.getAcquisitions());
      if (acquisitionIds.length > 0) {
        return Object.keys(this.getWells(acquisitionIds[0])).length;
      }
      return 0;
    }

      /**
       * Counts the number of sites in the first well of the first acquisition. Assumes that the structure is consistent across the plate.
       * @returns {number} The count of sites in the first well of the first acquisition, or 0 if none are found.
       */
      countSites() {
        const acquisitionIds = Object.keys(this.getAcquisitions());
        if (acquisitionIds.length > 0) {
          const firstWellKey = this.getFirstWellKey(acquisitionIds[0]);
          if (firstWellKey) {
            return Object.keys(this.getSites(acquisitionIds[0], firstWellKey)).length;
          }
        }
        return 0;
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

      static getWellName(row, col) {
        let rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h"];
        return rows[row] + col.toString().padStart(2, '0');
      }

      static getRowIndexFromWellName(name) {
        // Define valid rows again to align with getWellName
        const rows = [
          "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
          "a", "b", "c", "d", "e", "f", "g", "h"
        ];

        const rowChar = name[0];
        const rowIndex = rows.indexOf(rowChar);
        if (rowIndex === -1) {
          throw new Error(`Invalid well name: ${name}`);
        }

        return rowIndex;
      }

      static getColIndexFromWellName(name) {
        let colIndex = parseInt(name.substr(1), 10);
        return colIndex;
      }
  }

  class Plates {
    constructor(jsonData) {
      this.data = jsonData;
    }

    getPlate(index) {
      const plateData = this.data[Object.keys(this.data)[index]];
      return new Plate(plateData);
    }

    getFirstPlate() {
      return this.getPlate(0);
    }
  }

  var loaded_plates = null;
  var listed_plates = null;
  var animation = null;

  function initMainWindow(plateBarcode, acquisitionID) {
    selectBrightnessFromStoredValue();
    selectShowHiddenFromStoredValue();
    selectShowCompoundsFromStoredValue();
    apiListPlates();

    console.log("plateBarcode", plateBarcode);

    if (plateBarcode == "" && acquisitionID == "") {
      console.log("plateBarcode == '' && acquisitionID == '', Do nothing");
      // Do nothing
    } else if (acquisitionID != "") {
      apiLoadAcquisitionID(plateBarcode, acquisitionID);
    } else {
      apiLoadPlateBarcode(plateBarcode);
    }
  }

  function initViewerWindow(plate, acquisition, well, site, zpos, channel){
    selectBrightnessFromStoredValue();

    loadPlateFromViewer(plate, acquisition, well, site, zpos, channel);
  }


  function getLoadedPlate() {
    // return first (and only) plate
    return loaded_plates.getFirstPlate();
  }

  function apiListPlates() {

    document.getElementById("left-sidebar-spinner").style.visibility = "visible";

    let formData = new FormData(document.getElementById('query-form'));
    //formData.append("show-hidden-cb", getSelectedShowHiddenValue() );

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
    window.listed_plates = queryResults;
    drawPlatesListSidebar(queryResults);
  }

  function redrawPlatesListSidebar(){
      platesList =  window.listed_plates;
      if(platesList){
        drawPlatesListSidebar(platesList);
      }
  }

function filterchanged(){
  let filter = getSearchFilterText();
  if(filter.length == 0 || filter.length > 1 ){
    redrawPlatesListSidebar();
  }
}

function toggleSidebarSort(){
  setSortSidebar(! getSortSidebar());
  redrawPlatesListSidebar();
}

function drawPlatesListSidebar(origPlatesList) {
  console.log('origPlatesList', origPlatesList);

  // Make a deep copy of the original plates list to avoid modifying it
  let platesList = origPlatesList.map(plate => ({ ...plate }));

  // Clear and clone the list container
  let list = document.getElementById('result-list');
  document.getElementById('result-list').replaceWith(list.cloneNode(false)); // Ensure false is passed to cloneNode to not clone deep
  list = document.getElementById('result-list');

  // Helper function to remove all children from a node
  function removeChildren(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  // Clear the existing list
  removeChildren(list);

  // Filter logic based on search filter text
  let filter = getSearchFilterText().toLowerCase();
  if (filter.length > 0) {
    platesList = platesList.filter(row =>
      Object.values(row).some(value => String(value).toLowerCase().includes(filter))
    );
  }

  console.log("platesList", platesList);

  // Filter out hidden plates if necessary
  if (!getSelectedShowHiddenValue()) {
    platesList = platesList.filter(item => !item.hidden);
  }

  console.log("platesList", platesList);

  // Sorting platesList by date descending (or by id descending if date is unavailable)
  let sortedPlatesList;
  if (!filter) {
    sortedPlatesList = [...platesList].sort((a, b) => b.id - a.id);
  } else {
    sortedPlatesList = platesList;
  }

  // Identifying the latest acquisitions
  let latestAcquisitions = [];
  if (!filter) {
    const latestAcqCount = 10;
    latestAcquisitions = sortedPlatesList.slice(0, latestAcqCount);
  }

  console.log("sortedPlatesList", sortedPlatesList);
  console.log("latestAcquisitions", latestAcquisitions);

  // Group sorted plates by project
  let projects = {};
  sortedPlatesList.forEach(plate => {
    if (!projects[plate.project]) {
      projects[plate.project] = [];
    }
    projects[plate.project].push(plate);
  });

  // Function to create a list item for a plate
  function createPlateListItem(plate) {
    let plateItem = document.createElement('li');
    let link = document.createElement('a');
    link.className = "text-info";
    link.href = "#";
    link.title = `${plate.name} acq-id: ${plate.id} project: ${plate.project} micro: ${plate.microscope}`;
    link.textContent = plate.name;
    link.onclick = e => {
      e.preventDefault();
      apiLoadPlate(plate.plate_barcode, plate.id);
    };
    plateItem.appendChild(link);
    return plateItem;
  }

  // Add "Latest acquisitions" if not filtering
  let latestAcqItem = null;
  if (!filter && latestAcquisitions.length > 0) {
    latestAcqItem = document.createElement('li');
    latestAcqItem.innerHTML = "<span style='cursor: pointer;'>Latest acquisitions</span>";
    let latestAcqList = document.createElement('ul');
    latestAcquisitions.forEach(plate => latestAcqList.appendChild(createPlateListItem(plate)));
    latestAcqItem.appendChild(latestAcqList);
    list.appendChild(latestAcqItem);
  }

  // Define project keys array
  let projectKeys = Object.keys(projects);

  // Sort project names if sortSidebar is true
  if (getSortSidebar()) {
    projectKeys.sort();
  }

  // No need to sort plates within each project since they are already sorted
  // when we sorted sortedPlatesList

  // Add items for all projects
  projectKeys.forEach(projectName => {
    let projectItem = document.createElement('li');
    projectItem.innerHTML = `<span style='cursor: pointer;'>${projectName}</span>`;
    let projectPlateList = document.createElement('ul');
    projects[projectName].forEach(plate => projectPlateList.appendChild(createPlateListItem(plate)));
    projectItem.appendChild(projectPlateList);
    list.appendChild(projectItem);
  });

  // Turn sidebar list into a clickable tree-view with projects collapsed
  $('#result-list').bonsai({
    expandAll: false, // expand all items
    expand: null, // optional function to expand an item
    collapse: null, // optional function to collapse an item
    addExpandAll: false, // add a link to expand all items
    addSelectAll: false, // add a link to select all checkboxes
    selectAllExclude: null, // a filter selector or function for selectAll
    createInputs: false,
    checkboxes: false, // run quit(this.options) on the root node (requires jquery.qubit)
    handleDuplicateCheckboxes: false // update any other checkboxes that have the same value
  });

  // This is a tweak to make filter working
  $('#result-list').bonsai('update');

  // Expand "Latest acquisitions" by default
  if (latestAcqItem) {
    let bonsai = $('#result-list').data('bonsai');
    bonsai.expand(latestAcqItem);
  }

  // If result is less than 10 items, expand all
  if (platesList.length < 10) {
    let bonsai = $('#result-list').data('bonsai');
    bonsai.expandAll(list);
  }

  // Tweak to get clickable project names instead of only the little arrow
  $('#result-list').on('click', 'span', function () {
    console.log("click");
    $(this).closest('li').find('> .thumb').click();
  });

  // Activate tooltips within the result list
  $('#result-list [data-toggle="tooltip"]').tooltip({
    trigger: 'hover',
    boundary: 'window'
  });
}



function drawPlatesListSidebar_old(origPlatesList){

    console.log('origPlatesList', origPlatesList);

    // make a copy of platesList
    let platesList = origPlatesList.slice();

    // replace list idem with a new clone
    let list = document.getElementById('result-list');
    document.getElementById('result-list').replaceWith(list.cloneNode());
    list = document.getElementById('result-list');

    // Clear menu
    removeChildren(list);

    // Filter out plates depending on filter textfield
    let filter = getSearchFilterText().toLowerCase();
    console.log("filter", filter);
    if(filter.length > 0){
      let filteredList = [];
      platesList.forEach(function (row) {
        for (let value of Object.values(row)) {
          valueAsString = String(value).toLowerCase();
          if(valueAsString.indexOf(filter) > -1){
            filteredList.push(row);
            break;
          }
        }
      });
      console.log("filtered", filteredList);
      platesList = filteredList;
    }

    // if not showHidden, filter out hidden
    if(getSelectedShowHiddenValue() == false){
      platesList = platesList.filter(item => item.hidden != true);
    }

    // add "Latest acquisitions" sidebar item by adding plate aquisitions to top of
    // list with "Latest acquisitions" as project name

    latest_acq_len = 10

    // make copy of result array and sort it by acq_id
    acq_sorted = platesList.slice().sort((a, b) => {
      return a.id - b.id;
    });

    // get top xx results
    latest_results = acq_sorted.slice(-latest_acq_len).reverse();

    // insert copy of latesq acq-id in top of restlts with is_latest_acquisition = true
    latest_results.forEach(function (row) {
      row.is_latest_acquisition = true;
    });

    // Don't add latest aqc if filter is on
    if(!filter){
      platesList = latest_results.concat(platesList)
    }

    // create latest acq item and add it first on list
    let latest_acq_item = document.createElement('li');
    latest_acq_item.innerHTML = "<span style='cursor: pointer;''>" + "Latest acquisitions" + "</span>";
    let plate_list = document.createElement('ul');
    latest_acq_item.appendChild(plate_list);
    if(!filter){
      list.appendChild(latest_acq_item);
    }

    // create items for all plates (and projects as parents)
    let last_project = "";
    platesList.forEach((result, index) => {

      // Create a list with all projects
      let project = result.project;
      let proj = result.project;
      let plate_barcode = result.plate_barcode;
      let acq_name = result.name;
      let acq_id = result.id;
      let microscope = result.microscope;

      if(index < latest_results.length && !filter){
        // do nothing, we are still att "Latest acquisition" menu
        last_project = "lksdjfiweurehfkjbkjbs";
      }
      else if (last_project !== project) {
        let proj_item = document.createElement('li');
        proj_item.innerHTML = "<span style='cursor: pointer;''>" + project + "</span>";
        list.appendChild(proj_item);
        plate_list = document.createElement('ul');
        proj_item.appendChild(plate_list);
      }

      // Create a list item for the plate
      let plate_item = document.createElement('li');
      let link = document.createElement('a');
      let linktext = acq_name;
      let linkpopup_text = acq_name + " acq-id: " + acq_id + " project: " + proj + " micro: " + microscope;
      link.className = "text-info";
      link.href = "";

      //link.setAttribute("data-toggle", "tooltip");
      link.setAttribute("data-placement", "top"); // Placement has to be off element otherwise flicker
      link.setAttribute("data-delay", "0");
      link.setAttribute("data-animation", false);
      link.setAttribute("data-html", true);
      link.title = linkpopup_text;

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
      last_project = project;
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

    // This is a tweak to make filter working
    $('#result-list').bonsai('update');

    // Expand latest_acq by default
    let bonsai = $('#result-list').data('bonsai');
    bonsai.expand(latest_acq_item);

    // If result is < x items expand all
    if(platesList.length < 10){
      bonsai.expandAll(list);
    }

    // Tweak to get clickable project-names instead of only the little arrow
    // the project names are enclosed in <span></span>
    // https://github.com/aexmachina/jquery-bonsai/issues/23
    $('#result-list').on('click', 'span', function () {
      console.log("click");
      $(this).closest('li').find('> .thumb').click();
    });

    // Activate tooltips (all that have tooltip attribute within the resultlist)
    $('#result-list [data-toggle="tooltip"]').tooltip({
      trigger: 'hover',
      boundary: 'window'
    })
  }

  function apiLoadAcquisitionID(barcode, acq_id) {
    console.log("Inside apiLoadAcquisitionID: ", acq_id);
    apiLoadPlate(barcode, acq_id);
  }

  function apiLoadPlateBarcode(barcode) {
    console.log("Inside apiLoadPlateBarcode: ", barcode);
    apiLoadPlate(barcode);
  }

  function removeAllImages(container) {
    console.log("Inside removeAllImages");
    let images = container.getElementsByClassName('cellThumbImg');
    while (images.length > 0) {
        images[0].parentNode.removeChild(images[0]);
    }
  }

  function updateWindowURL(barcode, acq_id){
    window.history.pushState('', '', `?barcode=${barcode}&acqid=${acq_id}`);
  }


  function apiLoadPlate(plate_name, select_acq_id=undefined) {

    // stop any current animation
    stopAnimation();
    document.getElementById("animate-cbx").checked = false;

    // Remove all existing images
    let container = document.getElementById('plate-div');
    removeAllImages(container);

    url = '/api/plate/' + plate_name + '/' + select_acq_id
    fetch(url)
      .then(function (response) {
        if (response.status === 200) {

          //window.history.pushState('', '', url);
          updateWindowURL(plate_name, select_acq_id);

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

  function loadPlateFromViewer(plate_name, acquisition, well, site, zpos, channel) {

    console.log('plate_name', plate_name);
    console.log('channel', channel);

    // stop any current animation
    stopAnimation();
    document.getElementById("animate-cbx").checked = false;

    url = '/api/plate/' + plate_name + '/' + acquisition;
    fetch(url)
      .then(function (response) {
        if (response.status === 200) {

          response.json().then(function (json) {

            //window.history.pushState('', '', url);
            updateWindowURL(plate_name, acquisition);

            window.loaded_plates = new Plates(json['data'].plates);
            console.log(window.loaded_plates);
            updateToolbarWithNewPlate(acquisition, well, site, channel, zpos);
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

  function apiMoveAcquisitionToTrash(id) {
    console.log(`Moving Acquisition ID ${id} to trash.`);

    url = '/api/move-to-trash/' + id;
    fetch(url, { method: 'GET' })
      .then(function (response) {
        if (response.status === 200) {
          response.json().then(function (json) {

            console.log('response', json);
            console.log("AcqID trashed on server");
            getLoadedPlate().setProjectTrash(id);
            updateProjectNameLabel(getLoadedPlate())
            console.log("AcqID trashed on client");
            apiListPlates();
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

  function updateToolbarWithNewAcquisition() {
    updateWellSelect(getLoadedPlate());
    updateSiteSelect(getLoadedPlate());
    updateZSelect(getLoadedPlate());
    updateChannelSelect(getLoadedPlate());
    updatePlateAcqLabel(getLoadedPlate());
    updateProjectNameLabel(getLoadedPlate());
  }

  function updateToolbarWithNewPlate(selected_acq_id, selected_well, selected_site, selected_channel, selected_zpos){

    console.log("selected_well", selected_well);
    updateAcquisitionSelect(getLoadedPlate(), selected_acq_id);
    updateAcquisitionSlider(getLoadedPlate(selected_acq_id));
    updateWellSelect(getLoadedPlate(), selected_well);
    updateSiteSelect(getLoadedPlate(), selected_site);
    updateZSelect(getLoadedPlate(), selected_zpos);
    updateChannelSelect(getLoadedPlate(), selected_channel);
    updatePlateNameLabel(getLoadedPlate().getName());
    updateProjectNameLabel(getLoadedPlate());
    updatePlateAcqLabel(getLoadedPlate());

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
    let zpos = getSelectedZpos()[0];
    console.log("zpos", zpos);
    let channels = getLoadedPlate().getChannels(acquisition, well_name, site, zpos);
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
    let zpos = getSelectedZpos()[0];
    let channels = getLoadedPlate().getChannels(acquisition, well_name, site, zpos);
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

  function saveViewerImage(){

    console.log("inside saveViewerImage");

    // const canvasUrl = viewer.drawer.canvas.toDataURL("image/png");
    // const createEl = document.createElement('a');
    // createEl.href = canvasUrl;
    // createEl.download = "download-this-canvas";
    // createEl.click();
    // createEl.remove();

      // get what to redraw
      let acquisition = getSelectedAcquisition();
      let plate_name = getLoadedPlate().getName();
      console.log("acquisition", acquisition);

      // Image viewer hack since it only takes a single site
      let site = getSelectedSite()[0];
      console.log("site", site);
      let well_name = getSelectedWell();
      console.log("well_name", well_name);
      let zpos = getSelectedZpos()[0];
      let channels = getLoadedPlate().getChannels(acquisition, well_name, site, zpos);
      console.log("channels", channels);
      let imgURL = createMergeImgURLFromChannels(channels);

      console.log("imgUrl", imgURL);

      const createEl = document.createElement('a');
      createEl.href = imgURL;
      img_name = "img_" + plate_name + "_acqid_" + acquisition + "_" + well_name + "_site_" + site + "_merged"
      createEl.download = img_name;
      createEl.click();
      createEl.remove();

      //window.open(imgURL);

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
      let zpos = getSelectedZpos()[0];
      let channels = getLoadedPlate().getChannels(acquisitionID, well_name, site, zpos);
      let imgURL = createMergeImgURLFromChannels(channels);

      if (acquisitionIndex !== skipIndex) {
        addImageToViewer(acquisitionIndex, imgURL, 0);
      }
    }
  }

  function openViewer(well_name, site_name) {

    let acquisition = getSelectedAcquisition();
    // let site = getSelectedSiteIndex();
    let zpos = getSelectedZpos()[0];
    let channels = getLoadedPlate().getChannels(acquisition, well_name, site_name, zpos);
    let imgURL = createMergeImgURLFromChannels(channels);

    let viewerURL = "/image-viewer/" + getLoadedPlate().getName() +
      "/tp/" + acquisition +
      "/well/" + well_name +
      "/site/" + site_name +
      "/zpos/" + zpos +
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

    // get z to draw
    let zpos = getSelectedZpos();
    console.log("zpos", zpos)
    //zpos = zpos[0];

    drawPlate(plateObj, acquisition, site, zpos, clearFirst);

    drawImageAnalysisTableFiltered(plateObj)
  }

  function drawImageAnalysisTableFiltered(plateObj) {
    plate_barcode = plateObj.getName();
    apiCreateImageAnalysesTable(plate_barcode)
  }

  function createEmptyTable(rows, cols, sites, zpos, plateObj=null) {
    console.log('inside create empty plate');
    let isShowCompounds = getSelectedShowCompoundsValue();
    let table = document.createElement('table');
    table.id = 'plateTableOne';
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
      let well_name = Plate.getWellName(row, col);
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

        let well_name = Plate.getWellName(row, col);

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

        let sites_table = create_site_layout(well_name, sites, zpos);

        let well_div = document.createElement("div");
        well_div.className = "wellDiv"
        well_div.id = "awelldiv"
        let site_div = document.createElement("div");
        site_div.className

        // if there is layout info for this well, add it
        if(plateObj){
          let well_meta_list = plateObj.getWellLayoutMeta(well_name);
          if (well_meta_list && well_meta_list.length > 0) {
            well_meta_list.forEach((well_meta, index) => {
              createLayoutInfoDiv(plateObj, well_div, well_name, well_meta, index, isShowCompounds);
            });
          }
        }

        well_div.title = well_name;
        well_div.appendChild(site_div);
        site_div.appendChild(sites_table);
        well_cell.appendChild(well_div);

      }
      table.appendChild(rowElement);

    }

    return table;
  }

  function createLayoutInfoDiv(plateObj, well_div, well_name, well_meta, index, isShowCompounds) {
    let layout_info_div = document.createElement("div");
    layout_info_div.className = "layoutInfoDotDiv";
    layout_info_div.id = `${well_name}_layoutinfodiv_${index}`;

    // Set tooltip attributes
    layout_info_div.setAttribute("data-toggle", "tooltip");
    layout_info_div.setAttribute("data-placement", "top");
    layout_info_div.setAttribute("data-delay", "0");
    layout_info_div.setAttribute("data-animation", false);
    layout_info_div.setAttribute("data-html", true);

    // Store the cbkid
    layout_info_div.setAttribute('data-cbkid', well_meta.cbkid);

    // Construct the tooltip title
    let title = `Well: ${well_meta.well_id}<br>` +
                `cbkid: ${well_meta.cbkid}<br>` +
                `batchid: ${well_meta.batch_id}<br>` +
                `compound-name: ${well_meta.compound_name}<br>` +
                `cmpd-conc: ${well_meta.cmpd_conc}<br>` +
                `pert-type: ${well_meta.pert_type}<br>` +
                `cells/well: ${well_meta.cells_per_well}<br>` +
                `cell-line: ${well_meta.cell_line}`;

    layout_info_div.title = title;
    layout_info_div.style.backgroundColor = color_from_cbkid(well_meta.cbkid);

    layout_info_div.style.visibility = isShowCompounds ? 'visible' : 'hidden';

    // Offset each layout_info_div by 30 pixels vertically
    layout_info_div.style.top = (index * 30) + 'px';

    // Event handlers for highlighting
    layout_info_div.onmouseover = function(evt) {
        if (well_meta && well_meta.cbkid) {
            highlight_all_info_div(well_meta.cbkid);
        }
    };

    layout_info_div.onmouseout = function(evt) {
        lowlight_all_info_div();
    };

    well_div.appendChild(layout_info_div);
  }

  const compColors = {
    "[fenb]": "#6666ff",
    "[ca-O]": "#d9d9d9",
    "[dmso]": "#ffec51",
    "[berb]": "#ff0000",
    "[flup]": "#cab968",
    "[tetr]": "#d9b28c",
    "[sorb]": "#c6ff1a",
    "[etop]": "#66ff66"
  }

  function color_from_cbkid(id){
    color = '#5d5d5d99'; //'#6c6c6c';
    if (id !== null && typeof id === "string") {
      if(id in compColors){
        color = compColors[id];
      }else if(id.startsWith('[')){
        color = "#66ff66";
      }
    }

    return color;
  }

  function highlight_all_info_div(cbkid) {
    Array.from(document.getElementsByClassName('layoutInfoDotDiv')).forEach(
        function(layout_info_div) {
            if (layout_info_div.getAttribute('data-cbkid') == cbkid) {
                layout_info_div.style.border = '6px solid white';
            }
        }
    );
  }

  function lowlight_all_info_div() {
    Array.from(document.getElementsByClassName('layoutInfoDotDiv')).forEach(
        function(layout_info_div) {
            layout_info_div.style.border = '1px solid grey';
        }
    );
  }


  function create_site_layout_old(well_name, sites, zpos){

    let table = document.createElement('table');
    table.id = 'siteTable';
    table.className = 'siteTable';

    // Now add rows and columns
    nSites = sites.length;
    nZpos = zpos[0].length;
    nPos = Math.max(nSites, nZpos);
    //console.log("nSites", nSites);


    nRows = Math.ceil(Math.sqrt(nSites));
    nCols = Math.ceil(Math.sqrt(nSites));

    for (let row = 0; row < nRows; row++) {
      let rowElement = document.createElement('tr');
      //rowElement.className = 'siteRow';
      for (let col = 0; col < nCols; col++) {

        nSite = col + row * nCols // This if you want column order: nSite = row + col * nCols

        //console.log("add site: " + nSite);

        let site_name = sites[nSite];
        let cell_name = well_name + "_s" + site_name + "_z" + zpos[0];

        let site_cell = document.createElement('td');
        site_cell.id = cell_name;
        site_cell.className = 'siteCell';
        rowElement.appendChild(site_cell);
      }
      table.appendChild(rowElement);

    }
    return table;

  }


  function create_site_layout(well_name, sites, zpos){

    let table = document.createElement('table');
    table.id = 'siteTable';
    table.className = 'siteTable';

    // Now add rows and columns
    nElements = sites.length * zpos.length
    nRows = Math.ceil(Math.sqrt(nElements));
    nCols = Math.ceil(Math.sqrt(nElements));

    // loop sites and zpos
    // Add the sites and zpos that are selected to be shown
    let cell_names = [];
    for(let siteIndex = 0; siteIndex < sites.length; siteIndex++) {
      for(let zposIndex = 0; zposIndex < zpos.length; zposIndex++) {
        let site_name = sites[siteIndex];
        cell_name = well_name + "_s" + site_name + "_z" + zpos[zposIndex];
        cell_names.push(cell_name);
      }
    }

    let cell_index = 0;
    for (let row = 0; row < nRows; row++) {
      let rowElement = document.createElement('tr');
      for (let col = 0; col < nCols; col++) {
        let cell_name = cell_names[cell_index];
        let site_cell = document.createElement('td');
        site_cell.id = cell_name;
        site_cell.className = 'siteCell';
        rowElement.appendChild(site_cell);
        cell_index ++;
      }
      table.appendChild(rowElement);

    }
    return table;

  }

  function drawPlate(plateObj, acquisition, sites, zpos, clearFirst) {

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

    let siteNames = sites; // plateObj.getSiteNames();

    // first create a new plate consisting of empty well-div's
    if (document.getElementById('plateTable') == null) {
      let plateSize = plateObj.getPlateSize(siteNames);
      let table = createEmptyTable(plateSize.rows, plateSize.cols, plateSize.sites, zpos, plateObj);
      container.appendChild(table);
      console.log('done create div');
    }

    console.log(container);

    console.log("acquisition", acquisition);

    // now populate well-div's with the wells of the plateobj
    let wells = plateObj.getWells(acquisition);
    Object.keys(wells).forEach(well_key => {
      let well = wells[well_key];

      // Add the sites and zpos that are selected to be shown
      for(let siteIndex = 0; siteIndex < siteNames.length; siteIndex++) {
        for(let zposIndex = 0; zposIndex < zpos.length; zposIndex++) {

          let site_name = siteNames[siteIndex];

          let site = well.sites[site_name];
          if(site != null){

            //console.log("site", site);

            let site_key = well_key + "_s" + site_name + "_z" + zpos[zposIndex];
            //console.log("site_key", site_key);
            let site_cell = document.getElementById(site_key);

            //console.log("siteNames", siteNames);
            //console.log("site_name", site_name);
            //console.log("well_key", well_key);

            // Try to get existing canvas - if it doesn't exist create it
            // this way we are only drawing images on top of existing images
            // and animation becomes smooth
            let siteCanvas = document.getElementById('siteCanvas' + site_key);
            if (siteCanvas == null) {

              siteCanvas = document.createElement('canvas');
              siteCanvas.className = 'siteCanvas';
              siteCanvas.id = 'siteCanvas' + site_key;
              siteCanvas.title = '' + site_key;

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


            //console.log('site', site);
            //console.log('zpos', zpos);
            //console.log('site.z_positions', site.z_positions);


            if(site && site.z_positions && site.z_positions && site.z_positions[zpos[0]] && site.z_positions[zpos[0]].channels != null){

              console.log("site.z_positions[zpos[0]].channels", site.z_positions[zpos[0]].channels);

              let url = createMergeThumbImgURLFromChannels(site.z_positions[zpos[0]].channels);
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
            }else{
              console.log('site.z_positions[zpos].channels is null')
            }

            // // Add tooltip when hoovering an image
            //  siteCanvas.setAttribute("data-toggle", "tooltip");
            //  siteCanvas.setAttribute("data-placement", "right"); // Placement has to be off element otherwise flicker
            //  siteCanvas.setAttribute("data-delay", "0");
            //  siteCanvas.setAttribute("data-animation", false);
            //  siteCanvas.setAttribute("data-html", true);
            //  siteCanvas.title = site_key; //plateObj.getFormattedWellMeta(acquisition, well_key);
          }
        }
      }

    })

    // Activate tooltips (all that have tooltip attribute within the resultlist)
     $('#plate-div [data-toggle="tooltip"]').tooltip({
       trigger : 'hover',
       boundary: 'window'
     });
  }

  function getSelectedAcquisitionIndex() {
    let elem = document.getElementById('acquisition-select');
    return elem.selectedIndex;
  }

  function getSelectedAcquisitionId() {
    let elem = document.getElementById('acquisition-select');
    if (!elem || elem.selectedIndex < 0 || elem.selectedIndex >= elem.options.length) {
      return null;
    }
    return getAcquisitionFromIndex(elem.selectedIndex);
  }


  function getAcquisitionFromIndex(index) {
    let elem = document.getElementById('acquisition-select');
    return elem.options[index].value;
  }

  function getSelectedAcquisition() {
    let elem = document.getElementById('acquisition-select');
    if (!elem || elem.options.length === 0) {
      return null;
    }
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

  function getSelectedShowHiddenValue() {
    return document.getElementById('show-hidden-cb').checked;
  }

  function getSelectedShowCompoundsValue() {
    console.log("compoundscb", document.getElementById('show-compounds-cb').checked);
    return document.getElementById('show-compounds-cb').checked;
  }

  function selectBrightnessFromStoredValue(){
    let brightness = getBrightness();
    console.log("brightness", brightness);
    let elem = document.getElementById('brightness-select');
    let index = getIndexFromValue(elem.options, brightness);
    elem.selectedIndex = index;
  }

  function selectShowHiddenFromStoredValue(){
    let showHidden = getShowHidden();
    console.log("showHidden", showHidden);
    document.getElementById('show-hidden-cb').checked = showHidden;
  }

  function selectShowCompoundsFromStoredValue(){
    let value = getShowCompounds();
    document.getElementById('show-compounds-cb').checked = value;
  }

  function getSearchFilterText(){
    return document.getElementById('search-textfield').value;
  }

  function clearFilterText(){
    document.getElementById('search-textfield').value = "";
    filterchanged();
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

  function getSelectedZpos() {
    //let allZ = getLoadedPlate().getAvailableZpos(getSelectedAcquisitionId());
    //return allZ[0];
    let elem  = document.getElementById('z-select');
    let zpos = JSON.parse(elem.options[elem.selectedIndex].value);
    return zpos;
  }

  function getSelectedWell() {
    let elem = document.getElementById('well-select');
    return elem.options[elem.selectedIndex].value;
  }

  function getSelectedAnimationSpeed() {
    let elem = document.getElementById('animation-speed-select');
    return parseInt(elem.options[elem.selectedIndex].value);
  }


  function updateAcquisitionSelect_old(plateObj, selected_acq_id=undefined) {
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

  function updateAcquisitionSelect(plateObj, selected_acq_id = undefined) {
    let elemSelect = document.getElementById('acquisition-select');

    // Reset
    elemSelect.options.length = 0;

    // Get acquisitions
    let acquisitions = Object.values(plateObj.getAcquisitions());

    for (let acquisition of acquisitions) {

        let selected = (selected_acq_id == acquisition.id);

        let title = "" + acquisition.id + "   -   " + acquisition.name;

        // Create option element
        let option = new Option(title, acquisition.id, selected, selected);

        // Set title attribute (not supported)
        //option.title = title;

        // Add option to select element
        elemSelect.options.add(option);
    }

    // Enable or disable if there is more than one option
    elemSelect.disabled = elemSelect.options.length <= 1;
    console.log("elemSelect.disabled", elemSelect.disabled);
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

  function setZSelection(z) {
    let elemSelect = document.getElementById('z-select');
    elemSelect.selectedIndex = getSelectIndexFromSelectValue(elemSelect, z);
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
    let siteNames = plateObj.getSiteNames(getSelectedAcquisitionId());

    // Loop through the siteNames array
    for (let name of siteNames) {
      option_json = "[" + name + "]";
      option_display = name;
      selected = (selected_site == option_json) ? true : false;
      elemSelect.add(new Option(option_display, option_json, selected, selected));
    }

    // finally add an "all" option
    let allOption = JSON.stringify(siteNames)
    elemSelect.add(new Option(allOption, allOption));
  }

  function updateZSelect(plateObj, selected_z) {
    let elemSelect = document.getElementById('z-select');

    // reset
    elemSelect.options.length = 0;

    // add as many options as zpos
    let z_positions = plateObj.getAvailableZpos(getSelectedAcquisitionId());

    // if z_selection not specified, select one in middle
    if (!selected_z && z_positions && z_positions.length > 0) {
      let middleIndex = Math.floor(z_positions.length / 2);
      selected_z = "[" + z_positions[middleIndex] + "]";
    }

    // Loop through the names array
    for (let zpos of z_positions) {
      option_json = "[" + zpos + "]";
      option_display = zpos;
      selected = (selected_z == option_json) ? true : false;
      elemSelect.add(new Option(option_display, option_json, selected, selected));
    }

    // finally add an "all" option
    if(z_positions && z_positions.length > 1){
      const allOption =  `[ ${z_positions.join(', ')} ]`;
      elemSelect.add(new Option(allOption, allOption));
    }
  }

  function updatePlateNameLabel(plate_name) {
    document.getElementById('plate-name-label').innerHTML = "Plate: " + plate_name;
    document.getElementById('plate-name-label').title = "Plate: " + plate_name;
  }

  function updateProjectNameLabel(plateObj) {
    let project_name = plateObj.getProjectName(getSelectedAcquisitionId())
    document.getElementById('project-name-label').innerHTML = "Proj: " + project_name;
    document.getElementById('project-name-label').title = "Proj: " + project_name;
  }

  function updatePlateAcqLabel(plateObj) {

    let plate_acq_id = getSelectedAcquisitionId()
    let title = "" + plateObj.getAcquisitionFolder(plate_acq_id);

    document.getElementById('acq-id-label').title = title;
  }

  function getChannelIdFromDye(dye, channels){

    for(const [key, value] of Object.entries(channels)){
      channel_name = value.dye;
      channel_id = value.id;
      if(dye === channel_name){
        return channel_id;
      }
    }
    return 0
  }

  function updateChannelSelect(plateObj, selected_channel) {
    let elemSelect = document.getElementById('channel-select');

    // reset
    elemSelect.options.length = 0;

    let channels = plateObj.getAvailableChannels(getSelectedAcquisitionId());

    let nCount = Object.keys(channels).length;

    // // First add default (Merge channels options)
    // if (nCount === 1) {
    //   elemSelect.options[0] = new Option("1", "1");
    // } else if (nCount === 2) {
    //   elemSelect.options[0] = new Option("H,M", "1,2");
    // } else if (Set()) {

    // }

    let channel_names = Object.values(channels).map(channel => channel.dye);
    let is_subset = ['HOECHST','MITO', 'PHAandWGA'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      r = getChannelIdFromDye('MITO', channels);
      g = getChannelIdFromDye('PHAandWGA', channels);
      elemSelect.add( new Option("H,M,P", "" + b + "," + r + "," + g) );
    }

    is_subset = ['HOECHST','PHAandWGA', 'SYTO'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      r = getChannelIdFromDye('PHAandWGA', channels);
      g = getChannelIdFromDye('SYTO', channels);
      elemSelect.add( new Option("H,P,S", "" + b + "," + r + "," + g) );
    }

    is_subset = ['HOECHST','MITO', 'DIOC6'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      r = getChannelIdFromDye('MITO', channels);
      g = getChannelIdFromDye('DIOC6', channels);
      elemSelect.options[0] = new Option("H,M,D", "" + b + "," + r + "," + g);
    }

    is_subset = ['NUCLEUS','MITO', 'ACTIN'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('NUCLEUS', channels);
      r = getChannelIdFromDye('MITO', channels);
      g = getChannelIdFromDye('ACTIN', channels);
      elemSelect.add (new Option("N,M,A", "" + b + "," + r + "," + g) );
    }

    is_subset = ['NUCLEUS','GOLGI', 'ACTIN'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('NUCLEUS', channels);
      r = getChannelIdFromDye('GOLGI', channels);
      g = getChannelIdFromDye('ACTIN', channels);
      elemSelect.add (new Option("N,G,A", "" + b + "," + r + "," + g) );
    }

    is_subset = ['HOECHST','MITO', 'PHA'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      r = getChannelIdFromDye('MITO', channels);
      g = getChannelIdFromDye('PHA', channels);
      elemSelect.add (new Option("H,M,P", "" + b + "," + r + "," + g) );
    }

    is_subset = ['HOECHST','MITO', 'SYTO'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      r = getChannelIdFromDye('MITO', channels);
      g = getChannelIdFromDye('SYTO', channels);
      elemSelect.add (new Option("H,M,S", "" + b + "," + r + "," + g) );
    }

    is_subset = ['HOECHST','CONC', 'PHAandWGA'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      r = getChannelIdFromDye('CONC', channels);
      g = getChannelIdFromDye('PHAandWGA', channels);
      elemSelect.add( new Option("H,C,P", "" + b + "," + r + "," + g) );
    }

    is_subset = ['HOECHST', 'PHAandWGA'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('HOECHST', channels);
      g = getChannelIdFromDye('PHAandWGA', channels);
      elemSelect.add( new Option("H,P", "" + b + "," + g) );
    }

    is_subset = ['BF', 'BFz1', 'BFz2'].every(val => channel_names.includes(val))
    if(is_subset){
      b = getChannelIdFromDye('BF', channels);
      r = getChannelIdFromDye('BFz1', channels);
      g = getChannelIdFromDye('BFz2', channels);
      elemSelect.add( new Option("BF,BFz1,BFz2", "" + b + "," + r + "," + g) );
    }

    // add as many options as channels
    for(const [key, value] of Object.entries(channels)){
      channel_name = value.dye;
      channel_id = value.id;
      option_text = "" + value.id + "-" + channel_name
      option_value = channel_id;
      elemSelect.add(new Option(option_text, option_value));
    }

    // set selected
    Array.from(elemSelect.options).forEach(option => {
      if (selected_channel === option.value) {
        option.selected = true;
      }
    });
  }



  function removeChildren(domObject) {
    if(domObject){
      while (domObject.firstChild) {
        domObject.removeChild(domObject.firstChild);
      }
    }
  }

  function createMergeThumbImgURLFromChannels(channels) {

    //console.log(channels, channels);
    if(!channels){
      return "/static/images/empty.png";
    }

    try{
      let value = String(getSelectedChannelValue());

      let selected = value.split(',');

      let url = null;
      if (selected.length == 2) {
        channel_blue = selected[0];
        channel_red = selected[1];
        url = "/api/image-merge-thumb/ch1/" + channels[channel_blue].path + "/ch2/" + channels[channel_red].path + "/ch3/" + 'undefined' + "/channels.png";
      } else if (selected.length == 3) {
        channel_blue = selected[0];
        channel_red = selected[1];
        channel_green = selected[2];
        url = "/api/image-merge-thumb/ch1/" + channels[channel_blue].path + "/ch2/" + channels[channel_red].path + "/ch3/" + channels[channel_green].path + "/channels.png";
      } else {
        let channel_grey = selected[0];
        url = "/api/image-merge-thumb/ch1/" + channels[channel_grey].path + "/ch2/" + 'undefined' + "/ch3/" + 'undefined' + "/channels.png"
      }

      return url;
    }catch(err){
      console.error(err);
      return "/static/images/empty.png";
     }
  }

  function createMergeImgURLFromChannels(channels) {

    console.log(channels, channels);
    if(!channels){
      return "/static/images/empty.png";
    }

    try{
      let value = String(getSelectedChannelValue());

      let selected = value.split(',');

      let url = null;
      if (selected.length == 2) {
        channel_blue = selected[0];
        channel_red = selected[1];
        url = "/api/image-merge/ch1/" + channels[channel_blue].path + "/ch2/" + channels[channel_red].path + "/ch3/" + 'undefined' + "/channels.png";
      } else if (selected.length == 3) {
        channel_blue = selected[0];
        channel_red = selected[1];
        channel_green = selected[2];
        url = "/api/image-merge/ch1/" + channels[channel_blue].path + "/ch2/" + channels[channel_red].path + "/ch3/" + channels[channel_green].path + "/channels.png";
      } else {
        let channel_grey = selected[0];
        url = "/api/image-merge/ch1/" + channels[channel_grey].path + "/ch2/" + 'undefined' + "/ch3/" + 'undefined' + "/channels.png"
      }

      return url;
    }catch(err){
      console.error(err);
      return "/static/images/empty.png";
     }
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

  function openTrashModal() {
    $('#trash-modal').modal('show');
  }

  function confirmMoveToTrash() {
    const enteredId = document.getElementById('confirm-id-input').value;
    const currentPlateAcquisitionId = getSelectedAcquisitionId();
    if (enteredId === currentPlateAcquisitionId) {
      $('#trash-modal').modal('hide');
      apiMoveAcquisitionToTrash(currentPlateAcquisitionId);
    } else {
      displayModalError('Plate acquisition does not match.');
    }
  }

  function zoomSelectChanged() {
    redrawPlate();
  }

  function brightnessSelectChanged() {
    let brightness = getSelectedBrightnessValue();
    setBrightness(brightness);
    redrawPlate();
  }

  function showHiddenSelectChanged() {
    let value = getSelectedShowHiddenValue();
    setShowHidden(value);
    redrawPlatesListSidebar();
    //location.reload();
  }

  function showCompoundsSelectChanged() {
    console.log('showCompoundsSelectChanged');
    let value = getSelectedShowCompoundsValue();
    setShowCompounds(value);
    setVisibility('infoDotDiv', value);
  }

  function setVisibility(className, value){

    Array.from(document.getElementsByClassName(className)).forEach(
      function(element, index, array) {

        if(value == true){
          //element.style.display = "inline-block";
          element.style.visibility = "visible";
        }
        else{
          //element.style.display = "none";
          element.style.visibility = "hidden";
        }
      }
    );
  }


  function acquisitionSelectChanged() {
    updateWindowURL(getLoadedPlate().getName(), getSelectedAcquisitionId());
    updateToolbarWithNewAcquisition();
    redrawPlate();
  }

  function siteSelectChanged() {
    redrawPlate();
  }

  function zSelectChanged() {
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

  function viewerZSelectChanged() {
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
    //rows = addFileLinksColumn(rows)

    // Before drawing table add "Segmentation link" to links column
    rows = addSegmentationLinkColumn(rows)

    // Truncate "result" column
    rows = truncateColumn(rows, "result", 100);

    drawTable(rows, "image_analyses-table-div");

  }

  function addSegmentationLinkColumn(rows){

    console.log("Inside Add addSegmentationLinkColumn");

    let BASE_URL = window.PIPELINEGUI_URL + "/";

    let cols = rows[0];

    // Define which column in result contains the result
    let id_col_index = cols.indexOf("id");
    let meta_col_index = cols.indexOf("meta");

    // Add header
    cols.splice(10, 0, "links");

    // Loop table rows
    // Start from row 1 (0 is headers)

    for (let nRow = 1; nRow < rows.length; nRow++) {

      let id = rows[nRow][id_col_index];
      let meta = rows[nRow][meta_col_index];

      let cell_contents = "";

      console.log("meta", meta);

      if(meta && meta['type'].indexOf("cp-features") > -1){

        console.log("meta", meta);

        let link_url = BASE_URL + "segmentation/" + id;
        cell_contents = "<a target='segmentation' href='" + link_url + "'>Segmentation</a>"
      }

      // insert cell
      rows[nRow].splice(10,0,cell_contents);

    }

    return rows;

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

  class LocalStorageStore {
    constructor() {
      this.defaults = {
        brightness: 100,
        showHidden: true,
        showCompounds: true,
        sortSidebar: false
      };
    }

    // Utility Methods
    get(name) {
      const item = localStorage.getItem(name);
      return item ? JSON.parse(item) : this.defaults[name];
    }

    set(name, value) {
      localStorage.setItem(name, JSON.stringify(value));
    }

    delete(name) {
      localStorage.removeItem(name);
    }

  }

  // Application-specific defaults and operations
  const storageStore = new LocalStorageStore();

  function setBrightness(value) {
    storageStore.set("brightness", value);
  }

  function getBrightness() {
    return storageStore.get("brightness");
  }

  function setShowHidden(value) {
    storageStore.set("showHidden", value);
  }

  function getShowHidden() {
    return storageStore.get("showHidden");
  }

  function setShowCompounds(value) {
    storageStore.set("showCompounds", value);
  }

  function getShowCompounds() {
    return storageStore.get("showCompounds");
  }

  function setSortSidebar(value) {
    storageStore.set("sortSidebar", value);
  }

  function getSortSidebar() {
    return storageStore.get("sortSidebar");
  }

/*
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
  */

