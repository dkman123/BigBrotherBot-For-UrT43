CREATE TABLE IF NOT EXISTS `iso_weapon` (
  `id` INT(11) UNSIGNED NOT NULL, -- AUTO_INCREMENT,
  `description` VARCHAR(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- insert records
INSERT INTO `iso_weapon` (id, description) VALUES ('1',  'MOD_WATER');
INSERT INTO `iso_weapon` (id, description) VALUES ('3',  'MOD_LAVA');
INSERT INTO `iso_weapon` (id, description) VALUES ('5',  'MOD_TELEFRAG');
INSERT INTO `iso_weapon` (id, description) VALUES ('6',  'MOD_FALLING');
INSERT INTO `iso_weapon` (id, description) VALUES ('7',  'MOD_SUICIDE');
INSERT INTO `iso_weapon` (id, description) VALUES ('9',  'MOD_TRIGGER_HURT');
INSERT INTO `iso_weapon` (id, description) VALUES ('10', 'MOD_CHANGE_TEAM');
INSERT INTO `iso_weapon` (id, description) VALUES ('12', 'KNIFE');
INSERT INTO `iso_weapon` (id, description) VALUES ('13', 'KNIFE_THROWN');
INSERT INTO `iso_weapon` (id, description) VALUES ('14', 'BERETTA');
INSERT INTO `iso_weapon` (id, description) VALUES ('15', 'DEAGLE');
INSERT INTO `iso_weapon` (id, description) VALUES ('16', 'SPAS');
INSERT INTO `iso_weapon` (id, description) VALUES ('17', 'UMP45');
INSERT INTO `iso_weapon` (id, description) VALUES ('18', 'MP5K');
INSERT INTO `iso_weapon` (id, description) VALUES ('19', 'LR300');
INSERT INTO `iso_weapon` (id, description) VALUES ('20', 'G36');
INSERT INTO `iso_weapon` (id, description) VALUES ('21', 'PSG1');
INSERT INTO `iso_weapon` (id, description) VALUES ('22', 'HK69');
INSERT INTO `iso_weapon` (id, description) VALUES ('23', 'BLED');
INSERT INTO `iso_weapon` (id, description) VALUES ('24', 'KICKED');
INSERT INTO `iso_weapon` (id, description) VALUES ('25', 'HE_GRENADE');
INSERT INTO `iso_weapon` (id, description) VALUES ('28', 'SR8');
INSERT INTO `iso_weapon` (id, description) VALUES ('30', 'AK103');
INSERT INTO `iso_weapon` (id, description) VALUES ('31', 'SPLODED');
INSERT INTO `iso_weapon` (id, description) VALUES ('32', 'SLAPPED');
INSERT INTO `iso_weapon` (id, description) VALUES ('33', 'SMITED');
INSERT INTO `iso_weapon` (id, description) VALUES ('34', 'BOMBED');
INSERT INTO `iso_weapon` (id, description) VALUES ('35', 'NUKED');
INSERT INTO `iso_weapon` (id, description) VALUES ('36', 'NEGEV');
INSERT INTO `iso_weapon` (id, description) VALUES ('37', 'HK69_HIT');
INSERT INTO `iso_weapon` (id, description) VALUES ('38', 'M4');
INSERT INTO `iso_weapon` (id, description) VALUES ('39', 'GLOCK');
INSERT INTO `iso_weapon` (id, description) VALUES ('40', 'COLT1911');
INSERT INTO `iso_weapon` (id, description) VALUES ('41', 'MAC11');
INSERT INTO `iso_weapon` (id, description) VALUES ('42', 'FRF1');
INSERT INTO `iso_weapon` (id, description) VALUES ('43', 'BENELLI');
INSERT INTO `iso_weapon` (id, description) VALUES ('44', 'P90');
INSERT INTO `iso_weapon` (id, description) VALUES ('45', 'MAGNUM');
INSERT INTO `iso_weapon` (id, description) VALUES ('46', 'TOD50');
INSERT INTO `iso_weapon` (id, description) VALUES ('47', 'FLAG');
INSERT INTO `iso_weapon` (id, description) VALUES ('48', 'GOOMBA');
