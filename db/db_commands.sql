
  DROP TABLE images;
  CREATE TABLE images (
      project     text,
      plate       text,
      timepoint   int,
      well        text,
      site        int,
      channel     int,
      path        text,
      metadata    jsonb
  );

  CREATE INDEX  ix_project ON images(project);
  CREATE INDEX  ix_plate ON images(plate);
  CREATE INDEX  ix_timepoint ON images(timepoint);
  CREATE INDEX  ix_well ON images(well);
  CREATE INDEX  ix_site ON images(site);
  CREATE INDEX  ix_channel ON images(channel);
  CREATE INDEX  ix_path ON images(path);
