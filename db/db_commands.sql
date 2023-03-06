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
    plate_barcode           text,
    timepoint               int,
    well                    text,
    site                    int,
    channel                 int,
    path                    text,
    file_meta               jsonb,
    metadata                jsonb,
    plate_acquisition_name  text
);

CREATE INDEX  ix_images_plate_acquisition_id ON images(plate_acquisition_id);
CREATE INDEX  ix_images_project ON images(project);
CREATE INDEX  ix_images_plate_barcode ON images(plate_barcode);
CREATE INDEX  ix_images_timepoint ON images(timepoint);
CREATE INDEX  ix_images_well ON images(well);
CREATE INDEX  ix_images_site ON images(site);
CREATE INDEX  ix_images_channel ON images(channel);
CREATE INDEX  ix_images_path ON images(path);
CREATE INDEX  ix_images_project_plate_barcode ON images(project, plate_barcode);
CREATE INDEX  ix_images_plate_acquisition_name ON images(plate_acquisition_name);
CREATE INDEX  ix_images_plate_barcode_textsearch ON images USING GIN (to_tsvector('english', plate_barcode));
CREATE INDEX  ix_images_plate_acquisition_name_textsearch ON images USING GIN (to_tsvector('english', plate_acquisition_name));

-- ALTER TABLE images ADD COLUMN plate_acquisition_name text;
-- UPDATE images SET plate_acquisition_name=plate_barcode;


DROP TABLE IF EXISTS plate_acquisition CASCADE;
CREATE TABLE plate_acquisition (
  id                serial PRIMARY KEY,
  plate_barcode     text,
  imaged            timestamp,
  microscope        text,
  channel_map_id    int,
  timepoint         int,
  folder            text
  name              text,
  project           text,
  finished          timestamp
);
CREATE INDEX ix_plate_acquisition_plate_barcode ON plate_acquisition(plate_barcode);
CREATE INDEX ix_plate_acquisition_channel_map_id ON plate_acquisition(channel_map_id);
CREATE INDEX ix_plate_acquisition_microscope ON plate_acquisition(microscope);
CREATE INDEX ix_plate_acquisition_folder ON plate_acquisition(folder);
CREATE INDEX ix_plate_acquisition_name ON plate_acquisition(name);
CREATE INDEX ix_plate_acquisition_project ON plate_acquisition(project);
CREATE INDEX ix_plate_acquisition_imaged ON plate_acquisition(imaged);
CREATE INDEX ix_plate_acquisition_finished ON plate_acquisition(finished);


CREATE OR REPLACE VIEW plate_acquisition_v1 AS
  SELECT
    id,
    name,
    plate_barcode,
    project,
    imaged,
    microscope,
    channel_map_id,
    timepoint,
    folder
  FROM plate_acquisition;

-- ALTER TABLE plate_acquisition ADD COLUMN name text;
-- UPDATE plate_acquisition SET name=plate_barcode;

-- ALTER TABLE plate_acquisition ADD COLUMN project text;
-- UPDATE plate_acquisition
-- SET project = images.project
-- FROM images
-- WHERE plate_acquisition.id = images.plate_acquisition_id;


DROP TABLE IF EXISTS new_plate_acquisition CASCADE;
CREATE TABLE new_plate_acquisition (
  id                int PRIMARY KEY,
  folder            text
);
CREATE INDEX ix_new_plate_acquisition_folder ON new_plate_acquisition(folder);


DROP TABLE IF EXISTS  channel_map CASCADE;
CREATE TABLE channel_map (
  map_id       int,
  channel      int,
  dye          text,
  name         text
);
CREATE INDEX  ix_channel_map_id ON channel_map(map_id);
CREATE INDEX  ix_channel_map_name ON channel_map(name);

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(1,	1,	'HOECHST',		'channel_map_1'),
(1,	2,	'CONC',	     	'channel_map_1'),
(1,	3,	'SYTO', 			'channel_map_1'),
(1,	4,	'MITO', 			'channel_map_1'),
(1,	5,	'PHAandWGA',  'channel_map_1');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(2,	1,	'HOECHST',		'channel_map_2'),
(2,	2,	'MITO',	     	'channel_map_2'),
(2,	3,	'PHAandWGA', 			'channel_map_2'),
(2,	4,	'SYTO', 			'channel_map_2'),
(2,	5,	'CONC',  'channel_map_2');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(3,	1,	'HOECHST',		'channel_map_3'),
(3,	2,	'PHA',	'channel_map_3');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(8,	1,	'HOECHST',		'channel_map_3'),
(8,	2,	'PHA',	'channel_map_3');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(8,	1,	'CELL',		'channel_map_8'),
(8,	2,	'CASP',		'channel_map_8'),
(8,	3,	'TOTO3',		'channel_map_8'),
(8,	4,	'HOECHST',		'channel_map_8'),
(8,	5,	'MITO',		'channel_map_8'),
(8,	6,	'DIOC6',	'channel_map_8');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(9,	1,	'HOECHST',		'channel_map_9'),
(9,	4,	'MITO',	     	'channel_map_9'),
(9,	3,	'PHAandWGA', 			'channel_map_9'),
(9,	5,	'SYTO', 			'channel_map_9'),
(9,	2,	'CONC',  'channel_map_9');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(10,	1,	'HOECHST',		'channel_map_10_squid'),
(10,	2,	'SYTO', 			'channel_map_10_squid'),
(10,	3,	'PHAandWGA', 			'channel_map_10_squid'),
(10,	4,	'MITO',	     	'channel_map_10_squid'),
(10,	5,	'CONC',  'channel_map_10_squid');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(11,	1,	'HOECHST',		'channel_map_11_only3'),
(11,	2,	'MITO', 			'channel_map_11_only3'),
(11,	3,	'PHAandWGA', 			'channel_map_11_only3');

INSERT INTO "channel_map" ("map_id", "channel", "dye", "name") VALUES
(12,	1,	'HOECHST',		'channel_map_12_IMX_comp_cent'),
(12,	2,	'CONC', 			'channel_map_12_IMX_comp_cent'),
(12,	3,	'SYTO', 			'channel_map_12_IMX_comp_cent'),
(12,	4,	'MITO',	     	'channel_map_10_squid'),
(12,	5,	'PHAandWGA',  'channel_map_12_IMX_comp_cent');

DROP TABLE IF EXISTS  channel_map_mapping CASCADE;
CREATE TABLE channel_map_mapping (
  project text,
  plate_acquisition_name  text,
  channel_map     int
);
CREATE INDEX  ix_channel_map_mapping_plate_acquisition_name ON channel_map_mapping(plate_acquisition_name);
CREATE INDEX  ix_channel_map_mapping_channel_map ON channel_map_mapping(channel_map);
CREATE INDEX  ix_channel_map_mapping_project ON channel_map_mapping(channprojectel_map);

INSERT INTO "channel_map_mapping" ("plate_acquisition_name", "channel_map") VALUES
('exp180-subset', 8);

INSERT INTO "channel_map_mapping" ("plate_acquisition_name", "channel_map") VALUES
('exp180', 8);

INSERT INTO "channel_map_mapping" ("plate_acquisition_name", "channel_map") VALUES
('cell-density-martin-2022-09-23', 10);

INSERT INTO "channel_map_mapping" ("plate_acquisition_name", "channel_map") VALUES
('BioTek-FA-U2OS-24h', 11);

INSERT INTO "channel_map_mapping" ("plate_acquisition_name", "channel_map") VALUES
('Bluewasher-FA-U2OS-24h', 11);


---> Import channel-map map
---> Then Update:
UPDATE plate_acquisition
   SET channel_map_id = channel_map_mapping.channel_map
   FROM channel_map_mapping WHERE plate_acquisition.name = channel_map_mapping.plate_acquisition_name;

UPDATE plate_acquisition
   SET channel_map_id = channel_map_mapping.channel_map
   FROM channel_map_mapping WHERE plate_acquisition.project = channel_map_mapping.project;



CREATE OR REPLACE VIEW images_all_view AS
  SELECT
    plate_acquisition.project,
    images.plate_acquisition_id,
    plate_acquisition.name AS plate_acquisition_name,
    plate_acquisition.plate_barcode,
    images.id AS image_id,
    images.timepoint,
    images.well,
    images.site,
    images.channel,
    images.path,
    plate_acquisition.imaged,
    plate_acquisition.microscope,
    plate_acquisition.channel_map_id,
    channel_map.dye,
    plate.size,
    plate.seeded,
    plate.cell_line,
    plate.cells_per_well,
    plate.type AS plate_type,
    plate.treatment,
    plate.treatment_units,
    plate.painted,
    plate.painted_type,
    plate_layout.layout_id,
    plate_layout.solvent,
    plate_layout.stock_conc,
    plate_layout.pert_type,
    plate_layout.batch_id,
    plate_layout.cmpd_vol,
    plate_layout.well_vol,
    plate_layout.cmpd_conc,
    compound.batchid,
    compound.name AS compound_name,
    compound.cbkid,
    compound.libid,
    compound.libtxt,
    compound.smiles,
    compound.inchi,
    compound.inkey
   FROM (((((images
     LEFT JOIN plate_acquisition ON ((images.plate_acquisition_id = plate_acquisition.id)))
     LEFT JOIN channel_map ON (((plate_acquisition.channel_map_id = channel_map.map_id) AND (images.channel = channel_map.channel))))
     LEFT JOIN plate ON ((images.plate_barcode = plate.barcode)))
     LEFT JOIN plate_layout ON (((plate.layout_id = plate_layout.layout_id) AND (plate_layout.well_id = images.well))))
     LEFT JOIN compound ON ((plate_layout.batch_id = compound.batchid)));

CREATE OR REPLACE VIEW images_minimal_view AS
SELECT
    images.id,
    images.plate_acquisition_id,
    plate_acquisition.project,
    images.plate_barcode,
    images.timepoint,
    images.well,
    images.site,
    images.channel,
    images.path,
    plate.size,
    plate.cell_line,
    plate.cells_per_well,
    plate_layout.layout_id,
    plate_layout.solvent,
    plate_layout.stock_conc,
    compound.batchid,
    compound.inchi,
    plate_acquisition.imaged,
    plate_acquisition.microscope,
    plate_acquisition.channel_map_id,
    channel_map.map_id,
    channel_map.dye
   FROM (((((images
     LEFT JOIN plate_acquisition ON ((images.plate_acquisition_id = plate_acquisition.id)))
     LEFT JOIN channel_map ON (((plate_acquisition.channel_map_id = channel_map.map_id) AND (images.channel = channel_map.channel))))
     LEFT JOIN plate ON ((images.plate_barcode = plate.barcode)))
     LEFT JOIN plate_layout ON (((plate.layout_id = plate_layout.layout_id) AND (plate_layout.well_id = images.well))))
     LEFT JOIN compound ON ((plate_layout.batch_id = compound.batchid)));


-- Other tables

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
    result                jsonb,
    submitted             timestamp,
    priority              int
);

CREATE INDEX  ix_image_analyses_plate_acquisition_id ON image_analyses(plate_acquisition_id);
CREATE INDEX  ix_image_analyses_start ON image_analyses(start);
CREATE INDEX  ix_image_analyses_finish ON image_analyses(finish);
CREATE INDEX  ix_image_analyses_submitted ON image_analyses(submitted);
CREATE INDEX  ix_image_analyses_priority ON image_analyses(priority);

-- UPDATE image_analyses
-- SET meta = jsonb_set(coalesce(meta,{}),'{type}','"cp_features"',true)
-- WHERE pipeline_name like '%FEAT%'

-- UPDATE image_analyses
-- SET meta = jsonb_set(coalesce(meta,'{}'),'{type}','"cp_qc"',true)
-- WHERE pipeline_name like '%QC%'



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
    result                jsonb,
    priority              int
);

CREATE INDEX  ix_image_sub_analyses_analysis_id ON image_sub_analyses(analysis_id);
CREATE INDEX  ix_image_sub_analyses_start ON image_sub_analyses(start);
CREATE INDEX  ix_image_sub_analyses_finish ON image_sub_analyses(finish);
CREATE INDEX  ix_image_sub_analyses_priority ON image_sub_analyses(priority);


DROP TABLE IF EXISTS image_analyses_automation CASCADE;
CREATE TABLE image_analyses_automation (
    project               text,
    cell_line             text,
    pipeline_name         text,
    channel_map           int
);

CREATE INDEX  ix_image_analyses_automation_project ON image_analyses_automation(project);
CREATE INDEX  ix_image_analyses_automation_cell_line ON image_analyses_automation(cell_line);
CREATE INDEX  ix_image_analyses_automation_pipeline_name ON image_analyses_automation(pipeline_name);
CREATE INDEX  ix_image_analyses_channel_map ON image_analyses_automation(channel_map);


DROP TABLE IF EXISTS image_analyses_automation_submitted CASCADE;
CREATE TABLE image_analyses_automation_submitted (
    plate_acq_id          int,
    time                  timestamp
);

ALTER TABLE image_analyses_automation_submitted ADD CONSTRAINT constr_primary_key_image_analyses_automation_submitted_plate_acq_id PRIMARY KEY (plate_acq_id);

INSERT INTO image_analyses_automation_submitted (plate_acq_id)
  SELECT id FROM plate_acquisition

DELETE FROM image_analyses_automation_submitted
WHERE plate_acq_id = 2199

UPDATE image_analyses
SET meta = '{"type": "cp-qc"}'
WHERE id IN (
   SELECT id
   FROM image_analyses
   WHERE pipeline_name LIKE '%QC%'
   AND meta IS null
)

UPDATE image_analyses
SET meta = '{"type": "cp-features"}'
WHERE id IN (
   SELECT id
   FROM image_analyses
   WHERE pipeline_name LIKE '%FEAT%'
   AND meta IS null
)


DROP TABLE IF EXISTS imageset;
CREATE TABLE imageset (
    name                  text,
    plate_acquisition_id  int
);

CREATE INDEX  ix_imageset_name ON imageset(name);
CREATE INDEX  ix_imageset_plate_acquisition_id ON imageset(plate_acquisition_id);
ALTER TABLE imageset ADD CONSTRAINT constr_primary_key_imageset_name_plate_acquisition_id PRIMARY KEY (name, plate_acquisition_id);

CREATE OR REPLACE VIEW imageset_images_all_view AS
  SELECT
        imageset.name AS imageset_name,
        images.*
    FROM
        images
    RIGHT JOIN imageset ON imageset.plate_acquisition_id = images.plate_acquisition_id
;


CREATE OR REPLACE VIEW image_analyses_v1 AS
  SELECT
        image_analyses.id AS id,
        image_analyses.pipeline_name AS pipeline_name,
        plate_acquisition.project AS project,
        plate_acquisition.id AS plate_acquisition_id,
        plate_acquisition.plate_barcode AS plate_barcode,
        image_analyses.start at time zone 'cet' AS start,
        image_analyses.finish at time zone 'cet' AS finish,
        image_analyses.error at time zone 'cet' AS error,
        image_analyses.meta AS meta,
        image_analyses.depends_on_id AS depends_on_id,
        image_analyses.result AS result
    FROM
        plate_acquisition
    RIGHT JOIN image_analyses ON image_analyses.plate_acquisition_id = plate_acquisition.id
;

CREATE OR REPLACE VIEW image_analyses_per_plate AS
  SELECT
        plate_acquisition.project,
        plate_acquisition.plate_barcode AS plate_barcode,
        plate_acquisition.name AS plate_acq_name,
        plate_acquisition.id AS plate_acq_id,
        image_analyses.id AS analysis_id,
        to_char(image_analyses.finish at time zone 'cet', 'YYYY-MM-DD')  AS analysis_date,
        to_char(image_analyses.error at time zone 'cet', 'YYYY-MM-DD') AS analysis_error,
        image_analyses.meta AS meta,
        image_analyses.pipeline_name,
        CONCAT('/share/data/cellprofiler/automation/',image_analyses.result::json->>'job_folder') AS results
    FROM
        plate_acquisition
    LEFT JOIN image_analyses ON image_analyses.plate_acquisition_id = plate_acquisition.id
;

-- SELECT * FROM image_analyses_per_plate
-- ORDER BY project, plate_barcode, plate_acq_name, meta, analysis_date
--
-- SELECT project, plate_acq_name, meta, analysis_date, analysis_error, pipeline_name, plate_acq_id, analysis_id, results
-- FROM image_analyses_per_plate
-- ORDER BY project, plate_barcode, plate_acq_name, meta, analysis_date


CREATE OR REPLACE VIEW image_sub_analyses_v1 AS
  SELECT
        image_sub_analyses.sub_id AS sub_id,
        image_analyses.id AS analyses_id,
        image_analyses.pipeline_name AS pipeline_name,
        plate_acquisition.id AS plate_acquisition_id,
        plate_acquisition.plate_barcode AS plate_barcode,
        image_sub_analyses.start at time zone 'cet' AS start,
        image_sub_analyses.finish at time zone 'cet' AS finish,
        image_sub_analyses.error at time zone 'cet' AS error,
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

INSERT INTO "plate_acquisition" ("id", "plate_barcode", "imaged", "microscope", "channel_map_id", "timepoint", "folder") VALUES
(-1,	'debug_plate_001',	'1970-01-01',	'ImageXpress',	1,	1, '/share/mikro/IMX/MDC_pharmbio/exp-combTox-new/BJ-48hr-1/');


-- labdesign-tables

DROP TABLE IF EXISTS plate_layout CASCADE;
CREATE TABLE plate_layout (
    layout_id               text,
    well_id                 text,
    batch_id                text,
    solvent                 text,
    stock_conc              decimal,
    stock_conc_unit         text,
    cmpd_vol                decimal,
    cmpd_vol_unit           text,
    well_vol                decimal,
    well_vol_unit           text,
    pert_type               text,
    cmpd_conc               decimal,
    cmpd_conc_unit          text,
    cell_line               text,
    cells_per_well          numeric
);

CREATE INDEX  ix_plate_layout_layout_id ON plate_layout(layout_id);
CREATE INDEX  ix_plate_layout_well_id ON plate_layout(well_id);
CREATE INDEX  ix_plate_layout_batch_id ON plate_layout(batch_id);
CREATE INDEX  ix_plate_layout_pert_type ON plate_layout(pert_type);
CREATE INDEX  ix_plate_layout_cell_line ON plate_layout(cell_line);
CREATE INDEX  ix_plate_layout_cells_per_well ON plate_layout(cells_per_well);

ALTER TABLE plate_layout ADD CONSTRAINT constr_primary_key_plate_layout_layout_id_well_id PRIMARY KEY (layout_id, well_id);

DROP VIEW plate_layout_v1;
CREATE OR REPLACE VIEW plate_layout_v1 AS
  SELECT
    plate_layout.layout_id,
    plate_layout.well_id,
    plate_layout.batch_id,
    plate_layout.solvent,
    plate_layout.stock_conc,
    plate_layout.stock_conc_unit,
    plate_layout.cmpd_vol,
    plate_layout.cmpd_vol_unit,
    plate_layout.well_vol,
    plate_layout.well_vol_unit,
    plate_layout.pert_type,
    plate_layout.cmpd_conc,
    plate_layout.cmpd_conc_unit,
    plate_layout.cell_line,
    plate_layout.cells_per_well,
    compound.batchid,
    compound.cbkid,
    compound.libid,
    compound.libtxt,
    compound.name,
    compound.smiles,
    compound.inchi,
    compound.inkey
  FROM
      plate_layout
  LEFT JOIN compound ON plate_layout.batch_id = compound.batchid;



DROP TABLE IF EXISTS plate CASCADE;
CREATE TABLE plate (
  layout_id               text,
  barcode                 text PRIMARY KEY,
  type                    text,
  size                    int,
  seeded                  timestamp,
  cell_line               text,
  cells_per_well          numeric,
  treatment               text,
  treatment_units         text,
  painted                 timestamp,
  painted_type            text
);

CREATE INDEX  ix_plate_layout_id ON plate(layout_id);
CREATE INDEX  ix_plate_barcode ON plate(barcode);
CREATE INDEX  ix_plate_size ON plate(size);
CREATE INDEX  ix_plate_seeded ON plate(seeded);
CREATE INDEX  ix_plate_cell_line ON plate(cell_line);
CREATE INDEX  ix_plate_treatment ON plate(treatment);
CREATE INDEX  ix_plate_treatment_units ON plate(treatment_units);
CREATE INDEX  ix_plate_painted ON plate(painted);


-- INSERT INTO plate (plate_barcode)
-- SELECT DISTINCT(plate_barcode) FROM images;

DROP VIEW plate_v1;
CREATE OR REPLACE VIEW plate_v1 AS
  SELECT
    plate.barcode,
    plate.size,
    plate.seeded,
    plate.type AS plate_type,
    plate.treatment,
    plate.treatment_units,
    plate.painted,
    plate.painted_type,
    plate_layout.well_id,
    plate_layout.layout_id,
    plate_layout.solvent,
    plate_layout.stock_conc,
    plate_layout.pert_type,
    plate_layout.batch_id,
    plate_layout.cmpd_vol,
    plate_layout.well_vol,
    plate_layout.cmpd_conc,
    plate_layout.cell_line,
    plate_layout.cells_per_well,
    compound.batchid,
    compound.name AS compound_name,
    compound.cbkid,
    compound.libid,
    compound.libtxt,
    compound.smiles,
    compound.inchi,
    compound.inkey
  FROM plate
LEFT JOIN plate_layout ON (plate.layout_id = plate_layout.layout_id)
LEFT JOIN compound ON plate_layout.batch_id = compound.batchid;



-- well...
DROP TABLE IF EXISTS well CASCADE;
CREATE TABLE well (
    serial_id             serial UNIQUE,
    plate_barcode         text,
    well_id       	      text,
    cell_line             text,
    cell_passage          text,
    cell_density_perwell  int,
    treatment_h           int,
    PRIMARY KEY(plate_barcode, well_id)
);
CREATE INDEX ix_well_plate_barcode ON well(plate_barcode);
CREATE INDEX ix_well_well_id ON well(well_id);



DROP TABLE IF EXISTS  compound CASCADE;
CREATE TABLE compound (
  batchid         text,
  cbkid           text,
  libid           text,
  libtxt          text,
  smiles          text,
  inchi           text,
  inkey           text,
  name            text,
);
CREATE INDEX  ix_compound_batchid ON compound(batchid);
CREATE INDEX  ix_compound_cbkid   ON compound(cbkid);
CREATE INDEX  ix_compound_libid   ON compound(libid);
CREATE INDEX  ix_compound_libtxt  ON compound(libtxt);
CREATE INDEX  ix_compound_smiles  ON compound(smiles);
CREATE INDEX  ix_compound_inchi   ON compound(inchi);
CREATE INDEX  ix_compound_inkey   ON compound(inkey);
CREATE INDEX  ix_compound_name    ON compound(name);

CREATE TABLE compound_extra(
   batchid            text,
   pubchem_CID        text,
   CasNr              text,
   synonym            text,
   description        text,
   link               text,
   pubchem_SID        text,
   morph_change       text,
   pert_type          text,
   project            text,
   external_id        text,
   BRD_id             text,
   BRD_moa            text,
   BRD_target         text,
   BRD_disease_area   text,
   BRD_indication     text,
   seleck_target      text,
   seleck_pathway     text
);

CREATE INDEX  ix_compound_extra_batchid ON compound_extra(batchid);



DROP TABLE IF EXISTS project CASCADE;
CREATE TABLE project (
    name                    text PRIMARY KEY,
    description             text
);

CREATE INDEX  project_description_idx ON project USING GIN (to_tsvector('english', description));

INSERT INTO project (name)
SELECT DISTINCT(project) FROM images;

-- Until project database GUI is editable a view is replacing table
CREATE OR REPLACE VIEW project AS
  SELECT DISTINCT(project) AS name, '' AS description
  FROM plate_acquisition
  WHERE project IS NOT NULL




DROP TABLE IF EXISTS experiment CASCADE;
CREATE TABLE experiment (
    id                      serial PRIMARY KEY,
    name                    text,
    project                 text,
    creation_time           timestamp,
    description             text
);

CREATE INDEX  experiment_name_idx ON experiment(description);
CREATE INDEX  experiment_project_idx ON experiment(project);
CREATE INDEX  experiment_description_idx ON experiment USING GIN (to_tsvector('english', description));

INSERT INTO experiment (name, project, creation_time, description) VALUES
('version_1',	'2020_11_04_CPJUMP1',	current_timestamp, 'Description here'),
('version_2',	'2020_11_04_CPJUMP1', current_timestamp,'Description here');


DROP TABLE IF EXISTS plate_design CASCADE;
CREATE TABLE plate_design (
    name                    text PRIMARY KEY,
    config                  jsonb,
    creation_time           timestamp,
    description             text
);

CREATE INDEX  plate_design_description_idx ON plate_design USING GIN (to_tsvector('english', description));




CREATE OR REPLACE VIEW well_all_view AS
  SELECT
    plate.barcode AS plate_barcode,
    plate.seeded AS plate_seeded,
    plate.painted AS plate_painted,
    plate.size AS plate_size,
    plate.plate_layout_id,
    plate_layout.well_id,
    plate_layout.cmpd_id,
    plate_layout.solvent,
    plate_layout.stock_conc,
    plate_layout.stock_conc_unit,
    plate_layout.cmpd_conc,
    plate_layout.cmpd_conc_unit,
    plate_layout.dmso_conc_perc,
    plate_layout.pert_type,
    plate_layout.morph_change,
    compound.batchid,
    compound.cbkid,
    compound.libid,
    compound.libtxt,
    compound.smiles,
    compound.inchi,
    compound.inkey,
    well.serial_id AS serial_id,
    well.cell_line,
    well.cell_passage,
    well.cell_density_perwell,
    well.treatment_h
  FROM
      plate
  LEFT JOIN plate_layout ON plate.plate_layout_id = plate_layout.layout_id
  LEFT JOIN compound ON plate_layout.cmpd_id = compound.batchid
  LEFT JOIN well ON plate.barcode = well.plate_barcode AND plate_layout.well_id = well.well_id;


-- Some misc commands


-- Add readonly user
CREATE USER pharmbio_readonly WITH PASSWORD 'readonly';
GRANT CONNECT ON DATABASE imagedb TO pharmbio_readonly;
GRANT USAGE ON SCHEMA public TO pharmbio_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO pharmbio_readonly;
-- Allow user to access all tables, including ones not created yet (might not work)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT SELECT ON TABLES TO pharmbio_readonly;


-- From pod terminal, log in with client and copy a file to remote database (from a pod to server)
psql "dbname=imagedb user=postgres host=imagedb-pg-postgresql.services.svc.cluster.local"
\copy compound FROM '/home/jovyan/cbcs_tested.tsv' DELIMITER E'\t' CSV HEADER;


-- some jsonb
SELECT
jsonb_set(meta, '{analysis_meta}', '{"type":"cp-features"}'::jsonb)
FROM analysis_pipelines
where meta->'analysis_meta'->'type' = 'cp_features'
