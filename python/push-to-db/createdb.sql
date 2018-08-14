create table topicmsg ( 
  id integer primary key, 
  topic text,
  message text,
  qos integer,
  rectime integer,
  tsname text 
);

CREATE UNIQUE INDEX idx_topicmsg ON topicmsg(topic);

create table ts_cab (
  id integer primary key,
  topic text,
  message text,
  qos integer,
  rectime integer
);

create table ts_salon (
  id integer primary key,
  topic text,
  message text,
  qos integer,
  rectime integer
);

create table ts_chauf (
  id integer primary key,
  topic text,
  message text,
  qos integer,
  rectime integer
);

create table ts_connect (
  id integer primary key,
  topic text,
  message text,
  qos integer,
  rectime integer
);
