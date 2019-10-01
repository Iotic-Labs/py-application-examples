
CREATE TABLE qaconfig(
    ownuser_id     INT NOT NULL,
    host           VARCHAR(256)            NOT NULL,
    vhost          VARCHAR(256)            NOT NULL,
    prefix         VARCHAR(256)            NOT NULL,
    epId           VARCHAR(256)            NOT NULL,
    passwd         VARCHAR(256)            NOT NULL,
    token          VARCHAR(256)            NOT NULL,
    authtoken      VARCHAR(256)            NOT NULL,
    PRIMARY KEY (ownuser_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;
