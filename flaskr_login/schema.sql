drop table if exists post;
create table post(
id integer primary  key autoincrement,
title string not null,
text string not null
);