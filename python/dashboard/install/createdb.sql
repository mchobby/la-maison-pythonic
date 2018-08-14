create table application ( 
  id integer primary key, 
  label text not null
);

create table dashes (
  id integer primary key,
  label text not null,
  icon text,
  color text not null,
  color_text text
);

create table dash_blocks (
  id integer primary key,
  dash_id integer not null,
  title text not null,
  icon text,
  color text,
  color_text text, 
  block_type text not null,
  block_config text,
  source text not null,
  topic text not null,
  hist_type text,
  hist_size integer,

  FOREIGN KEY (dash_id) REFERENCES dashes(id)
);
