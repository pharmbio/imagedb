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

DROP TABLE IF EXISTS images;
CREATE TABLE images (
    id                      SERIAL,
    plate_acquisition_id    int,
    project                 text,
    plate                   text,
    timepoint               int,
    well                    text,
    site                    int,
    channel                 int,
    path                    text,
    metadata                jsonb
);

CREATE INDEX  ix_images_project ON images(project);
CREATE INDEX  ix_images_plate ON images(plate);
CREATE INDEX  ix_images_timepoint ON images(timepoint);
CREATE INDEX  ix_images_well ON images(well);
CREATE INDEX  ix_images_site ON images(site);
CREATE INDEX  ix_images_channel ON images(channel);
CREATE INDEX  ix_images_path ON images(path);

DROP TABLE IF EXISTS plate CASCADE;
CREATE TABLE plate (
  id                    SERIAL,
  barcode               text,
  seeded                timestamp,
  painted               timestamp
);
CREATE INDEX  ix_plate_barcode ON plate(barcode);

DROP TABLE IF EXISTS plate_acquisition CASCADE;
CREATE TABLE plate_acquisition (
  id              SERIAL,
  barcode         text,
  imaged          timestamp,
  microscope      text,
  channel_map_id  int,
  timepoint       int
);
CREATE INDEX  ix_plate_acquisition_barcode ON plate_acquisition(barcode);
CREATE INDEX  ix_plate_acquisition_channel_map ON plate_acquisition(channel_map);


-- well
DROP TABLE IF EXISTS well CASCADE;
CREATE TABLE well (
    id                    SERIAL,
    plate_barcode         text,
    well_name      	      text,
    well_role             text,
    comp_id               text,
    comp_conc_um          int,
    tot_well_vol_ul       int,
    cell_line             text,
    cell_passage          text,
    cell_density_perwell  int,
    treatment_h           int
);
CREATE INDEX  ix_well_id ON well(plate_barcode);
CREATE INDEX  ix_well_position ON well(well_name);


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


CREATE OR REPLACE VIEW images_all_view AS
  SELECT
      images.*,
      plate.*,
      well.*,
      channel_map.dye
  FROM
      images
  LEFT JOIN plate ON images.plate = plate.barcode
  LEFT JOIN well ON plate.barcode = well.plate_barcode AND images.well = well.well_name
  LEFT JOIN plate_acquisition on plate.barcode = plate_acquisition.barcode
  LEFT JOIN channel_map ON plate_acquisition.channel_map_id = channel_map.map_id AND images.channel = channel_map.channel;

CREATE OR REPLACE VIEW images_minimal_view AS
  SELECT
      project,
      plate,
      timepoint,
      well,
      well_role,
      comp_id,
      site,
      images.channel,
      channel_map.dye,
      path
  FROM
      images
  LEFT JOIN plate ON images.plate = plate.barcode
  LEFT JOIN well ON plate.barcode = well.plate_barcode AND images.well = well.well_name
  LEFT JOIN plate_acquisition ON plate.barcode = plate_acquisition.barcode
  LEFT JOIN channel_map ON plate_acquisition.channel_map_id = channel_map.map_id AND images.channel = channel_map.channel;




-- Other tables

DROP TABLE plate_map;
CREATE TABLE plate_map (
    map_id          int,
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

CREATE INDEX  ix_plate_map_map_id ON plate_map(map_id);
CREATE INDEX  ix_plate_map_well_position ON plate_map(well_position);

DROP TABLE plateold;
CREATE TABLE plateold (
  plate_map_id          int,
  channel_map_id        int,
  barcode               text,
  cell_line             text,
  cell_passage          text,
  cell_density_perwell  int,
  seeded                timestamp,
  painted               timestamp,
  imaged                timestamp
);

CREATE INDEX  ix_plateold_plate_map_id ON plateold(plate_map_id);
CREATE INDEX  ix_plateold_channel_map_id ON plateold(channel_map_id);
CREATE INDEX  ix_plateold_barcode ON plateold(barcode);

CREATE OR REPLACE VIEW plate_new_view AS
  SELECT
        barcode,
        seeded,
        painted,
        imaged,
        channel_map_id AS channel_map
  FROM
      plateold;

CREATE TABLE plate_map (
    map_id          int,
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

DROP VIEW well_new_view;
CREATE OR REPLACE VIEW well_new_view AS
  SELECT
      images.timepoint AS timepoint,
      images.site AS site,
      images.channel AS channel,
      plateold.barcode AS plate_barcode,
      plate_map.well_position AS well_name,
      well_role,
      cmpd_id AS comp_id,
      cmpd_conc_um AS comp_conc_um,
      tot_well_vol_ul,
      plateold.cell_line,
      plateold.cell_passage,
      plateold.cell_density_perwell,
      treatment_h
  FROM
      images
  LEFT JOIN plateold ON images.plate = plateold.barcode
  LEFT JOIN plate_map ON plateold.plate_map_id = plate_map.map_id AND images.well = plate_map.well_position
  LEFT JOIN channel_map ON plateold.channel_map_id = channel_map.map_id AND images.channel = channel_map.channel
  ;

  SELECT * FROM "well_new_view" WHERE plate_barcode is not null LIMIT 50;

UPDATE images
SET project = substring(path FROM '/share/mikro/IMX/MDC_pharmbio/(.*?)/');

UPDATE images
SET plate = substring(path FROM '/share/mikro/IMX/MDC_pharmbio/.*?/(.*?)/');



DROP TABLE image_analyses;
CREATE TABLE image_analyses (
    id                    SERIAL,
    plate_acquisition_id  int,
    pipeline_id           int,
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




DROP TABLE image_sub_analyses;
CREATE TABLE image_sub_analyses (
    sub_id                SERIAL,
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
        plate_acquisition.id AS plate_acquisition_id,
        plate_acquisition.barcode AS barcode,
        image_analyses.id AS image_analyses_id,
        image_sub_analyses.sub_id AS image_sub_analyses_sub_id
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



DROP TABLE IF EXISTS pipeline_automation;
CREATE TABLE pipeline_automation (
    id                SERIAL,
    match_pattern     text,
    pipeline          text
);

CREATE INDEX  ix_pipeline_automation_id ON pipeline_automation(id);


--INSERT INTO "image_analyses" ("plate_acquisition_id", "start", "finish", "error", "meta", "depends_on_id", "result") VALUES ('3', NULL, NULL, NULL, NULL, NULL, NULL);


-- INSERT INTO "image_sub_analyses" ("analysis_id", "plate_acquisition_id", "start", "finish", "error", "meta", "depends_on_sub_id", "result") VALUES ('1', '3', NULL, NULL, NULL, '{"cellprofiler": {"batching": 1, "pipeline": "/cpp_work/pipelines/debug.cppipe"}}', NULL, NULL);
