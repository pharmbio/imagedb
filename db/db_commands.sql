-- Good SQL queries
EXPLAIN (ANALYZE, BUFFERS) SELECT * from images_all_view WHERE plate = 'P009095'

EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT plate, project
FROM images
ORDER BY project, plate

-- list all pg server conf params
SHOW ALL


-- Create database, tables, index, viwes
CREATE DATABASE imagedb;

-- Log in to new database
\c imagedb;

DROP TABLE IF EXISTS images CASCADE;
CREATE TABLE images (
    id                      bigserial PRIMARY KEY,
    plate_acquisition_id    serial,
    project                 text,
    plate_barcode           text,
    timepoint               int,
    well                    text,
    site                    int,
    channel                 int,
    path                    text,
    file_meta               jsonb,
    metadata                jsonb
);

CREATE INDEX  ix_images_plate_acquisition_id ON images(plate_acquisition_id);
CREATE INDEX  ix_images_project ON images(project);
CREATE INDEX  ix_images_plate_barcode ON images(plate_barcode);
CREATE INDEX  ix_images_timepoint ON images(timepoint);
CREATE INDEX  ix_images_well ON images(well);
CREATE INDEX  ix_images_site ON images(site);
CREATE INDEX  ix_images_channel ON images(channel);
CREATE INDEX  ix_images_path ON images(path);

DROP TABLE IF EXISTS plate CASCADE;
CREATE TABLE plate (
  barcode               text PRIMARY KEY,
  seeded                timestamp,
  painted               timestamp,
  size                  text,
  plate_map_id          int         
);
CREATE INDEX  ix_plate_barcode ON plate(barcode);
CREATE INDEX  ix_plate_seeded ON plate(seeded);
CREATE INDEX  ix_plate_painted ON plate(painted);
CREATE INDEX  ix_plate_size ON plate(size);

DROP TABLE IF EXISTS plate_acquisition CASCADE;
CREATE TABLE plate_acquisition (
  id              serial PRIMARY KEY,
  plate_barcode   text,
  imaged          timestamp,
  microscope      text,
  channel_map_id  int,
  timepoint       int
);
CREATE INDEX ix_plate_acquisition_plate_barcode ON plate_acquisition(plate_barcode);
CREATE INDEX ix_plate_acquisition_channel_map_id ON plate_acquisition(channel_map_id);


-- well
DROP TABLE IF EXISTS well CASCADE;
CREATE TABLE well (
    id                    serial UNIQUE,
    plate_barcode         text,
    well_name      	      text,
    well_role             text,
    comp_id               text,
    comp_conc_um          int,
    tot_well_vol_ul       int,
    cell_line             text,
    cell_passage          text,
    cell_density_perwell  int,
    treatment_h           int,
    PRIMARY KEY(plate_barcode, well_name)
);
CREATE INDEX  ix_well_plate_barcode ON well(plate_barcode);


DROP TABLE IF EXISTS  compound CASCADE;
CREATE TABLE compound (
  comp_id         text,
  batch_id        text,
  annotation      text,
  cmpd_form       text,
  stock_conc_mm   int,
  stock_vol_nl    int
);
CREATE INDEX  ix_compound_comp_id ON compound(comp_id);



DROP TABLE IF EXISTS  channel_map CASCADE;
CREATE TABLE channel_map (
  map_id       int,
  channel      int,
  dye          text
);
CREATE INDEX  ix_channel_map_map_id ON channel_map(map_id);

INSERT INTO "channel_map" ("map_id", "channel", "dye") VALUES
(1,	1,	'HOECHST'),
(1,	2,	'MITO'),
(1,	3,	'PHALLOIDINandWGA'),
(1,	4,	'SYTO'),
(1,	5,	'CONCANAVALIN');


CREATE OR REPLACE VIEW images_all_view AS
  SELECT
    images.id as id,
    images.plate_acquisition_id,
    images.project,
    images.plate_barcode,
    images.timepoint,
    images.well,
    images.site,
    images.channel,
    images.path,
    images.metadata,
    well.well_name,
    well.well_role,
    well.comp_id,
    well.comp_conc_um,
    well.tot_well_vol_ul,
    well.cell_line,
    well.cell_passage,
    well.cell_density_perwell,
    well.treatment_h,
    plate_acquisition.imaged,
    plate_acquisition.microscope,
    plate_acquisition.channel_map_id,
    channel_map.map_id,
    channel_map.dye
  FROM
      images
  LEFT JOIN plate ON images.plate_barcode = plate.barcode
  LEFT JOIN well ON plate.barcode = well.plate_barcode AND images.well = well.well_name
  LEFT JOIN plate_acquisition on plate.barcode = plate_acquisition.plate_barcode
  LEFT JOIN channel_map ON plate_acquisition.channel_map_id = channel_map.map_id AND images.channel = channel_map.channel;

CREATE OR REPLACE VIEW images_minimal_view AS
  SELECT
    images.id as id,
    images.plate_acquisition_id,
    images.project,
    images.plate_barcode,
    images.timepoint,
    images.well,
    images.site,
    images.channel,
    images.path,
    well.well_role,
    well.comp_id,
    well.comp_conc_um,
    well.tot_well_vol_ul,
    well.cell_line,
    well.cell_passage,
    well.cell_density_perwell,
    well.treatment_h,
    plate_acquisition.imaged,
    plate_acquisition.microscope,
    plate_acquisition.channel_map_id,
    channel_map.map_id,
    channel_map.dye
  FROM
      images
  LEFT JOIN plate ON images.plate_barcode = plate.barcode
  LEFT JOIN well ON plate.barcode = well.plate_barcode AND images.well = well.well_name
  LEFT JOIN plate_acquisition on plate.barcode = plate_acquisition.plate_barcode
  LEFT JOIN channel_map ON plate_acquisition.channel_map_id = channel_map.map_id AND images.channel = channel_map.channel;


-- Other tables

DROP TABLE IF EXISTS plate_map;
CREATE TABLE plate_map (
    id              serial PRIMARY KEY,
    well_position   text,
    well_letter     text,
    well_num        int,
    well_role       text,
    cmpd_id         text,
    batch_id        text,
    annotation      text,
    cmpd_form       text,
    stock_conc_mm   int,
    stock_vol_nl    int,
    cmpd_conc_um    int,
    tot_well_vol_ul int,
    treatment_h     int
);

CREATE INDEX  ix_plate_map_id ON plate_map(id);
CREATE INDEX  ix_plate_map_well_position ON plate_map(well_position);


DROP TABLE IF EXISTS image_analyses CASCADE;
CREATE TABLE image_analyses (
    id                    serial,
    plate_acquisition_id  serial,
    pipeline_name         text,
    start                 timestamp,
    finish                timestamp,
    error                 timestamp,
    meta                  jsonb,
    depends_on_id         jsonb, -- if the analysis depends on another analysis being done, otherwise null
    result                jsonb 
);

CREATE INDEX  ix_image_analyses_plate_acquisition_id ON image_analyses(plate_acquisition_id);
CREATE INDEX  ix_image_analyses_start ON image_analyses(start);
CREATE INDEX  ix_image_analyses_finish ON image_analyses(finish);




DROP TABLE IF EXISTS image_sub_analyses;
CREATE TABLE image_sub_analyses (
    sub_id                serial,
    analysis_id           int,
    plate_acquisition_id  int,
    start                 timestamp,
    finish                timestamp,
    error                 timestamp,
    meta                  jsonb,
    depends_on_sub_id     jsonb, -- if the analysis depends on another analysis being done, otherwise null
    result                jsonb 
);

CREATE INDEX  ix_image_sub_analyses_analysis_id ON image_sub_analyses(analysis_id);
CREATE INDEX  ix_image_sub_analyses_start ON image_sub_analyses(start);
CREATE INDEX  ix_image_sub_analyses_finish ON image_sub_analyses(finish);



CREATE OR REPLACE VIEW image_analyses_V1 AS
  SELECT
        image_analyses.id AS id,
        image_analyses.pipeline_name AS pipeline_name,
        plate_acquisition.id AS plate_acquisition_id,
        plate_acquisition.plate_barcode AS plate_barcode,
        image_analyses.start AS start,
        image_analyses.finish AS finish,
        image_analyses.error AS error,
        image_analyses.meta AS meta,
        image_analyses.depends_on_id AS depends_on_id,
        image_analyses.result AS result
    FROM
        plate_acquisition
    RIGHT JOIN image_analyses ON image_analyses.plate_acquisition_id = plate_acquisition.id
;


CREATE OR REPLACE VIEW image_sub_analyses_V1 AS
  SELECT
        image_sub_analyses.sub_id AS sub_id,
        image_analyses.id AS analyses_id,
        image_analyses.pipeline_name AS pipeline_name,
        plate_acquisition.id AS plate_acquisition_id,
        plate_acquisition.plate_barcode AS plate_barcode,
        image_sub_analyses.start AS start,
        image_sub_analyses.finish AS finish,
        image_sub_analyses.error AS error,
        image_sub_analyses.meta AS meta,
        image_sub_analyses.depends_on_sub_id AS depends_on_sub_id,
        image_sub_analyses.result AS result
    FROM
        plate_acquisition
    RIGHT JOIN image_analyses ON image_analyses.plate_acquisition_id = plate_acquisition.id
    RIGHT JOIN image_sub_analyses ON image_sub_analyses.analysis_id = image_analyses.id
;


DROP TABLE IF EXISTS analysis_pipelines;
CREATE TABLE analysis_pipelines (
    name        text PRIMARY KEY,
    meta        jsonb
);


CREATE TABLE pipeline_automation (
    id                SERIAL,
    match_pattern     text,
    pipeline          text
);

CREATE INDEX  ix_pipeline_automation_id ON pipeline_automation(id);


INSERT INTO "analysis_pipelines" ("name", "meta") VALUES
('Test03',	'[{"type": "cellprofiler", "batch_size": 1, "pipeline_file": "debug.cppipe"}, {"type": "cellprofiler", "batch_size": 1, "pipeline_file": "debug.cppipe"}]'),
('TestPolina01',	'[{"type": "cellprofiler", "batch_size": 1, "pipeline_file": "2_QC_Raw_Img-384rowA.cppipe"}]'),
('TestPolina02',	'[{"type": "cellprofiler", "batch_size": 1, "pipeline_file": "2_QC_Raw_Img-rowP.cppipe"}]');


INSERT INTO "images" ("project", "plate_barcode", "timepoint", "well", "site", "channel", "path", "file_meta", "metadata", "plate_acquisition_id") VALUES
('debug-proj',	'debug_plate_001',	1,	'C02',	2,	5,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w59D4F5BD0-16D2-4E0F-95B5-9216083AD500.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "400 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,1656,2,48261,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349453,17,9349461,19,4,20,0,21,9349469,22,9349469,23,9349469,24,9349477,26,0,27,624", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "624", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}',	'{"guid": "9D4F5BD0-16D2-4E0F-95B5-9216083AD500", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w59D4F5BD0-16D2-4E0F-95B5-9216083AD500.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 5, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s2_w59D4F5BD0-16D2-4E0F-95B5-9216083AD500.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "400 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,1656,2,48261,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349453,17,9349461,19,4,20,0,21,9349469,22,9349469,23,9349469,24,9349477,26,0,27,624", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "624", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}, "timepoint": 1, "date_month": 7, "wellsample": "2", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	2,	4,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w484A157FC-998F-4628-9874-D92F63E3F0C4.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "300 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,2174,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349448,17,9349456,19,4,20,0,21,9349464,22,9349464,23,9349464,24,9349472,26,0,27,536", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "536", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}',	'{"guid": "84A157FC-998F-4628-9874-D92F63E3F0C4", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w484A157FC-998F-4628-9874-D92F63E3F0C4.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 4, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s2_w484A157FC-998F-4628-9874-D92F63E3F0C4.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "300 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,2174,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349448,17,9349456,19,4,20,0,21,9349464,22,9349464,23,9349464,24,9349472,26,0,27,536", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "536", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}, "timepoint": 1, "date_month": 7, "wellsample": "2", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	2,	3,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w3CBCC8E7C-4260-4373-ABFC-C670A4CF1689.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "450 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,692", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "692", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.06"}',	'{"guid": "CBCC8E7C-4260-4373-ABFC-C670A4CF1689", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w3CBCC8E7C-4260-4373-ABFC-C670A4CF1689.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 3, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s2_w3CBCC8E7C-4260-4373-ABFC-C670A4CF1689.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "450 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,692", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "692", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.06"}, "timepoint": 1, "date_month": 7, "wellsample": "2", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	2,	1,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w13080EA3C-47C8-478F-B4F8-FF7B90BCCE20.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "200 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,49910,3,1,4,9349768,5,9349776,6,9349784,7,9349793,8,0,9,255,11,128,12,64,13,0,14,65535,15,43,16,9349802,17,9349810,19,4,20,0,21,9349818,22,9349818,23,9349818,24,9349826,26,0,27,447", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "LAF Performed": "1", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "LAF Elapsed Time": "749", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "LAF Well Bottom Success": "1", "LAF Plate Bottom Success": "1", "LAF Well Bottom Attempts": "1", "LAF Well Bottom Exposure": "30", "LAF Well Bottom Position": "11223.4", "LAF Plate Bottom Attempts": "1", "LAF Plate Bottom Exposure": "20", "LAF Plate Bottom Position": "10940.5", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "447", "LAF Well Bottom Exposure Attempts": "2", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01", "LAF Plate Bottom Exposure Attempts": "1"}',	'{"guid": "3080EA3C-47C8-478F-B4F8-FF7B90BCCE20", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w13080EA3C-47C8-478F-B4F8-FF7B90BCCE20.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 1, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s2_w13080EA3C-47C8-478F-B4F8-FF7B90BCCE20.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "200 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,49910,3,1,4,9349768,5,9349776,6,9349784,7,9349793,8,0,9,255,11,128,12,64,13,0,14,65535,15,43,16,9349802,17,9349810,19,4,20,0,21,9349818,22,9349818,23,9349818,24,9349826,26,0,27,447", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "LAF Performed": "1", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "LAF Elapsed Time": "749", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "LAF Well Bottom Success": "1", "LAF Plate Bottom Success": "1", "LAF Well Bottom Attempts": "1", "LAF Well Bottom Exposure": "30", "LAF Well Bottom Position": "11223.4", "LAF Plate Bottom Attempts": "1", "LAF Plate Bottom Exposure": "20", "LAF Plate Bottom Position": "10940.5", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "447", "LAF Well Bottom Exposure Attempts": "2", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01", "LAF Plate Bottom Exposure Attempts": "1"}, "timepoint": 1, "date_month": 7, "wellsample": "2", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	1,	5,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w5C4BA3AC9-23D0-40DB-B3CF-571D15008B5A.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "400 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,2035,2,55785,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349453,17,9349461,19,4,20,0,21,9349469,22,9349469,23,9349469,24,9349477,26,0,27,624", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "624", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}',	'{"guid": "C4BA3AC9-23D0-40DB-B3CF-571D15008B5A", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w5C4BA3AC9-23D0-40DB-B3CF-571D15008B5A.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 5, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s1_w5C4BA3AC9-23D0-40DB-B3CF-571D15008B5A.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "400 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,2035,2,55785,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349453,17,9349461,19,4,20,0,21,9349469,22,9349469,23,9349469,24,9349477,26,0,27,624", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "624", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}, "timepoint": 1, "date_month": 7, "wellsample": "1", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	1,	1,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w183ADECB7-95DD-4F25-B827-8E91F826ACC7.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "200 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,31777,3,1,4,9349807,5,9349815,6,9349823,7,9349832,8,0,9,255,11,128,12,64,13,0,14,65535,15,43,16,9349841,17,9349849,19,4,20,0,21,9349857,22,9349857,23,9349857,24,9349865,26,0,27,447", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "LAF Performed": "1", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "LAF Elapsed Time": "1045", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "LAF Well Bottom Success": "1", "LAF Plate Bottom Success": "1", "LAF Well Bottom Attempts": "1", "LAF Well Bottom Exposure": "240", "LAF Well Bottom Position": "11221", "LAF Plate Bottom Attempts": "1", "LAF Plate Bottom Exposure": "20", "LAF Plate Bottom Position": "10940.6", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "447", "LAF Well Bottom Exposure Adjusted": "184", "LAF Well Bottom Exposure Attempts": "3", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01", "LAF Plate Bottom Exposure Attempts": "1"}',	'{"guid": "83ADECB7-95DD-4F25-B827-8E91F826ACC7", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w183ADECB7-95DD-4F25-B827-8E91F826ACC7.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 1, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s1_w183ADECB7-95DD-4F25-B827-8E91F826ACC7.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "200 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,31777,3,1,4,9349807,5,9349815,6,9349823,7,9349832,8,0,9,255,11,128,12,64,13,0,14,65535,15,43,16,9349841,17,9349849,19,4,20,0,21,9349857,22,9349857,23,9349857,24,9349865,26,0,27,447", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "LAF Performed": "1", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "LAF Elapsed Time": "1045", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "LAF Well Bottom Success": "1", "LAF Plate Bottom Success": "1", "LAF Well Bottom Attempts": "1", "LAF Well Bottom Exposure": "240", "LAF Well Bottom Position": "11221", "LAF Plate Bottom Attempts": "1", "LAF Plate Bottom Exposure": "20", "LAF Plate Bottom Position": "10940.6", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "447", "LAF Well Bottom Exposure Adjusted": "184", "LAF Well Bottom Exposure Attempts": "3", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01", "LAF Plate Bottom Exposure Attempts": "1"}, "timepoint": 1, "date_month": 7, "wellsample": "1", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	1,	3,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w3EBD173E7-D52C-4949-B8F4-4BF86A30346A.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "450 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,692", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "692", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.06"}',	'{"guid": "EBD173E7-D52C-4949-B8F4-4BF86A30346A", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w3EBD173E7-D52C-4949-B8F4-4BF86A30346A.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 3, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s1_w3EBD173E7-D52C-4949-B8F4-4BF86A30346A.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "450 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,692", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "692", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.06"}, "timepoint": 1, "date_month": 7, "wellsample": "1", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	1,	4,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w482F59207-BF98-4667-9D1A-C5F3699E728A.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "300 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,2448,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349448,17,9349456,19,4,20,0,21,9349464,22,9349464,23,9349464,24,9349472,26,0,27,536", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "536", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}',	'{"guid": "82F59207-BF98-4667-9D1A-C5F3699E728A", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w482F59207-BF98-4667-9D1A-C5F3699E728A.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 4, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s1_w482F59207-BF98-4667-9D1A-C5F3699E728A.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "300 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,2448,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,20,16,9349448,17,9349456,19,4,20,0,21,9349464,22,9349464,23,9349464,24,9349472,26,0,27,536", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "536", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}, "timepoint": 1, "date_month": 7, "wellsample": "1", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	2,	2,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w2DBFB0A4C-99F6-49C3-AF77-BDF6FCB67774.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "120 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,593", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "593", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}',	'{"guid": "DBFB0A4C-99F6-49C3-AF77-BDF6FCB67774", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s2_w2DBFB0A4C-99F6-49C3-AF77-BDF6FCB67774.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 2, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s2_w2DBFB0A4C-99F6-49C3-AF77-BDF6FCB67774.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "120 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,593", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "593", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}, "timepoint": 1, "date_month": 7, "wellsample": "2", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1),
('debug-proj',	'debug_plate_001',	1,	'C02',	1,	2,	'/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w28259B8B5-D257-4F22-9395-56018B680C25.tif',	'{"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "120 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,593", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "593", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}',	'{"guid": "8259B8B5-D257-4F22-9395-56018B680C25", "path": "/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/2019-07-22/119/BJ-48hr-1_C02_s1_w28259B8B5-D257-4F22-9395-56018B680C25.tif", "well": "C02", "plate": "BJ-48hr-1", "channel": 2, "project": "exp-combTox-new", "filename": "BJ-48hr-1_C02_s1_w28259B8B5-D257-4F22-9395-56018B680C25.tif", "date_year": 2019, "extension": ".tif", "file_meta": {"Gain": "16-bit (low noise & high well capacity)", "Region": "2160 x 2160, offset at (200, 0)", "Binning": "1 x 1", "Shading": "Off", "Exposure": "120 ms", "Software": "MetaMorph 5.3.0.5", "Subtract": "Off", "Cooler On": "1", "Digitizer": "560 MHz - fastest readout", "FillOrder": "msb-to-lsb", "Tag 33628": "0,1,1,0,2,65535,3,1,4,9349414,5,9349422,6,9349430,7,9349439,8,0,9,255,11,128,12,64,13,0,14,65535,15,25,16,9349447,17,9349455,19,4,20,0,21,9349463,22,9349463,23,9349463,24,9349471,26,0,27,593", "cell line": "BJ", "Resolution": "72, 72 pixels/inch", "Rows/Strip": "1", "Bits/Sample": "16", "Temperature": "-0.44", "Subfile Type": "(0 = 0x0)", "Trigger Mode": "Normal (TIMED)", "Samples/Pixel": "1", "Experiment set": "exp-combTox-new", "Deconvolution NA": "0.45", "Deconvolution RI": "1", "Frames to Average": "1", "Compression Scheme": "None", "Electronic Shutter": "Rolling", "Planar Configuration": "single image plane", "Baseline Clamp Enabled": "Yes", "Photometric Interpretation": "min-is-black", "Deconvolution X Image Spacing": "0.334", "Deconvolution Y Image Spacing": "0.334", "Deconvolution Emissive Wavelength": "593", "Deconvolution Spherical Aberration": "0", "Deconvolution Wiener Filter KValue": "0.01"}, "timepoint": 1, "date_month": 7, "wellsample": "1", "is_thumbnail": false, "magnification": "48hr", "date_day_of_month": 22}',	-1);

INSERT INTO "plate_acquisition" ("id", "plate_barcode", "imaged", "microscope", "channel_map_id", "timepoint") VALUES
(-1,	'debug_plate_001',	'1970-01-01',	'ImageXpress',	1,	1);


