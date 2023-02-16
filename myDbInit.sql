create table Tari (
 id serial primary key,
 nume_tara varchar(50),
 latitudine double precision,
 longitudine double precision
);

create table Orase (
id serial primary key,
id_tara int,
nume_oras varchar(50),
latitudine double precision,
longitudine double precision,
constraint fk_tara foreign key(id_tara) references Tari(id) on delete cascade on update cascade);

create table Temperaturi (
id serial primary key,
valoare double precision,
timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
id_oras int,
constraint fk_oras foreign key(id_oras) references orase(id) on delete cascade on update cascade);

alter table Tari add unique (nume_tara);
alter table Orase add constraint OraseConstraint unique (id_tara, nume_oras);
alter table Temperaturi add constraint TempConstraint unique (id_oras, timestamp);