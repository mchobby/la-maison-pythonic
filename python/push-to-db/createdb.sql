create table topicmsg ( 
  id integer primary key, 
  topic text,
  message text,
  qos integer,
  rectime integer,
  tsname text 
);

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
