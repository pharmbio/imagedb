
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
