CREATE TABLE IF NOT EXISTS `tp_subd`.`Forum` (
	`user` VARCHAR(45) NOT NULL,
	`short_name` VARCHAR(45) NOT NULL,
	`name` VARCHAR(45) NOT NULL,
	`order` ENUM("desc", "asc") NOT NULL DEFAULT "desc",
	`limit` INT NOT NULL,
	`forum` VARCHAR(45) NOT NULL,
	`since_id` INT NOT NULL,
	`since` DATETIME NOT NULL,
	`related` ENUM("", "user") NOT NULL,
	CONSTRAINT forum_name UNIQUE (`name`, `short_name`)
);


CREATE TABLE IF NOT EXISTS `tp_subd`.`Post` (
	`user` VARCHAR(45) NOT NULL,
	`order` ENUM("desc", "asc") NOT NULL DEFAULT "desc",
	`thread` INT NOT NULL,
	`post` INT NOT NULL AUTO_INCREMENT,
	`parent` INT NULL DEFAULT NULL,
	`forum` VARCHAR(45) NOT NULL,
	`message` TEXT NOT NULL,
	`vote` CHAR(2) NOT NULL,
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`since` DATETIME NOT NULL,
	`related` ENUM ("", "user", "thread", "forum") NOT NULL,
	`limit` INT NOT NULL,
	`isSpam` BOOLEAN NOT NULL DEFAULT 0,
	`isEdited` BOOLEAN NOT NULL DEFAULT 0,
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isHighlighted` BOOLEAN NOT NULL DEFAULT 0,
	`isApproved` BOOLEAN NOT NULL DEFAULT 0,
	PRIMARY KEY (`post`)
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`User` (
	`since` DATETIME NOT NULL,
	`order` ENUM("desc", "asc") NOT NULL DEFAULT "desc",
	`user` VARCHAR(45) NOT NULL,
	`username` VARCHAR(45) NOT NULL,
	`follower` VARCHAR(45) NOT NULL,
	`wollowee` VARCHAR(45) NOT NULL,
	`name` VARCHAR(45) NOT NULL,
	`limit` INT NOT NULL,
	`since_id` INT NOT NULL,
	`email` VARCHAR(45) NOT NULL,
	`isAnonimus` BOOLEAN NOT NULL DEFAULT 0,
	`about` TEXT NOT NULL,
	PRIMARY KEY (`email`)
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`Thread` (
	`thread` INT NOT NULL AUTO_INCREMENT,
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isClosed` BOOLEAN NOT NULL DEFAULT 0,
	`message` TEXT NOT NULL,
	`user` VARCHAR(45) NOT NULL,
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`slug` VARCHAR(45) NOT NULL,
	`title` VARCHAR(45) NOT NULL,
	`limit` INT NOT NULL,
	`forum` VARCHAR(45) NOT NULL,
	`related` ENUM ("", "user", "forum") NOT NULL,
	`since` DATETIME NOT NULL,
	`order` ENUM("desc", "asc") NOT NULL DEFAULT "desc",
	`vote` ENUM("-1", "1") NULL,
	PRIMARY KEY (`thread`)
);

TRUNCATE TABLE `tp_subd`.`Forum`;
TRUNCATE TABLE `tp_subd`.`User`;
TRUNCATE TABLE `tp_subd`.`Post`;
TRUNCATE TABLE `tp_subd`.`Thread `;
