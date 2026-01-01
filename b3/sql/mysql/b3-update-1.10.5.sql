-- SQL code to update default B3 database tables to B3 version 1.10.5 --
-- --------------------------------------------------------

ALTER TABLE `mapconfig` ADD `gamemodes` VARCHAR(50) NOT NULL DEFAULT '';
ALTER TABLE `mapconfig` ADD `bot` TINYINT(1) NOT NULL DEFAULT '0';
