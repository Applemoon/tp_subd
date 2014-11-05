------------------
-- foreigh keys --
------------------

CREATE TABLE IF NOT EXISTS `tp_subd`.`User` (
	`user` INT NOT NULL AUTO_INCREMENT, -- user id
	`email` VARCHAR(45) NOT NULL, -- user email
	`name` VARCHAR(45) NOT NULL, -- user name
	`username` VARCHAR(45) NOT NULL, -- user name ???
	`isAnonymous` BOOLEAN NOT NULL DEFAULT 0,
	`about` TEXT NOT NULL,
	PRIMARY KEY (`user`),
	UNIQUE KEY (`email`)
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`Follower` (
	`follower` VARCHAR(45) NOT NULL, -- follower email
	`following` VARCHAR(45) NOT NULL, -- following email
	FOREIGN KEY (`follower`) REFERENCES `tp_subd`.`User`(`email`)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (`following`) REFERENCES `tp_subd`.`User`(`email`)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`Forum` (
	`forum` INT NOT NULL AUTO_INCREMENT, -- forum id
	`name` VARCHAR(45) NOT NULL, -- forum full name
	`short_name` VARCHAR(45) NOT NULL, -- forum short name
	`user` VARCHAR(45) NOT NULL, -- founder email
	PRIMARY KEY (`forum`),
	UNIQUE KEY (`name`), 
	UNIQUE KEY (`short_name`),
	FOREIGN KEY (`user`) REFERENCES `tp_subd`.`User`(`email`)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`Thread` (
	`thread` INT NOT NULL AUTO_INCREMENT, -- thread id
	`title` VARCHAR(45) NOT NULL, -- thread title
	`user` VARCHAR(45) NOT NULL, -- founder email
	`message` TEXT NOT NULL,
	`forum` VARCHAR(45) NOT NULL, -- parent forum short_name
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isClosed` BOOLEAN NOT NULL DEFAULT 0,
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`slug` VARCHAR(45) NOT NULL, -- ???????
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`points` INT NOT NULL DEFAULT 0,  -- ???????
	PRIMARY KEY (`thread`),
	FOREIGN KEY (`user`) REFERENCES `tp_subd`.`User`(`email`)
		ON UPDATE CASCADE
		ON DELETE RESTRICT,
	FOREIGN KEY (`forum`) REFERENCES `tp_subd`.`Forum`(`short_name`)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`Subscription` (
	`subscriber` VARCHAR(45) NOT NULL, -- subscriber email
	`thread` INT NOT NULL, -- thread id
	FOREIGN KEY (`subscriber`) REFERENCES `tp_subd`.`User`(`email`)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (`thread`) REFERENCES `tp_subd`.`Thread`(`thread`)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `tp_subd`.`Post` (
	`post` INT NOT NULL AUTO_INCREMENT, -- post id
	`user` VARCHAR(45) NOT NULL, -- author email
	`thread` INT NOT NULL, -- thread id
	`forum` VARCHAR(45) NOT NULL, -- forum short_name
	`message` TEXT NOT NULL,
	`parent` INT NULL DEFAULT NULL, -- parent post id
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`isSpam` BOOLEAN NOT NULL DEFAULT 0,
	`isEdited` BOOLEAN NOT NULL DEFAULT 0,
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isHighlighted` BOOLEAN NOT NULL DEFAULT 0,
	`isApproved` BOOLEAN NOT NULL DEFAULT 0,
	PRIMARY KEY (`post`),
	FOREIGN KEY (`user`) REFERENCES `tp_subd`.`User`(`email`)
		ON UPDATE CASCADE
		ON DELETE RESTRICT,
	FOREIGN KEY (`thread`) REFERENCES `tp_subd`.`Thread`(`thread`)
		ON UPDATE CASCADE
		ON DELETE RESTRICT,
	FOREIGN KEY (`forum`) REFERENCES `tp_subd`.`Forum`(`short_name`)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE `tp_subd`.`Forum`;
TRUNCATE TABLE `tp_subd`.`User`;
TRUNCATE TABLE `tp_subd`.`Post`;
TRUNCATE TABLE `tp_subd`.`Thread`;
TRUNCATE TABLE `tp_subd`.`Follower`;
TRUNCATE TABLE `tp_subd`.`Subscription`;
SET FOREIGN_KEY_CHECKS=1;



---------------------
-- no foreigh keys --
---------------------

CREATE TABLE IF NOT EXISTS `tp_subd`.`User` (
	`user` INT NOT NULL AUTO_INCREMENT, -- user id
	`email` VARCHAR(45) NOT NULL, -- user email
	`name` VARCHAR(45) NULL, -- user name
	`username` VARCHAR(45) NULL, -- user name ???
	`isAnonymous` BOOLEAN NOT NULL DEFAULT 0,
	`about` TEXT NULL,
	PRIMARY KEY (`user`),
	UNIQUE KEY (`email`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tp_subd`.`Follower` (
	`follower` VARCHAR(45) NOT NULL, -- follower email
	`following` VARCHAR(45) NOT NULL -- following email
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tp_subd`.`Forum` (
	`forum` INT NOT NULL AUTO_INCREMENT, -- forum id
	`name` VARCHAR(45) NOT NULL, -- forum full name
	`short_name` VARCHAR(45) NOT NULL, -- forum short name
	`user` VARCHAR(45) NOT NULL, -- founder email
	PRIMARY KEY (`forum`),
	UNIQUE KEY (`name`), 
	UNIQUE KEY (`short_name`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tp_subd`.`Thread` (
	`thread` INT NOT NULL AUTO_INCREMENT, -- thread id
	`title` VARCHAR(45) NOT NULL, -- thread title
	`user` VARCHAR(45) NOT NULL, -- founder email
	`message` TEXT NOT NULL,
	`forum` VARCHAR(45) NOT NULL, -- parent forum short_name
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isClosed` BOOLEAN NOT NULL DEFAULT 0,
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`slug` VARCHAR(45) NOT NULL, -- ???????
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`points` INT NOT NULL DEFAULT 0,  -- ???????
	PRIMARY KEY (`thread`),
	UNIQUE KEY (`title`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tp_subd`.`Subscription` (
	`subscriber` VARCHAR(45) NOT NULL, -- subscriber email
	`thread` INT NOT NULL -- thread id
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tp_subd`.`Post` (
	`post` INT NOT NULL AUTO_INCREMENT, -- post id
	`user` VARCHAR(45) NOT NULL, -- author email
	`thread` INT NOT NULL, -- thread id
	`forum` VARCHAR(45) NOT NULL, -- forum short_name
	`message` TEXT NOT NULL,
	`parent` INT NULL DEFAULT NULL, -- parent post id
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`isSpam` BOOLEAN NOT NULL DEFAULT 0,
	`isEdited` BOOLEAN NOT NULL DEFAULT 0,
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isHighlighted` BOOLEAN NOT NULL DEFAULT 0,
	`isApproved` BOOLEAN NOT NULL DEFAULT 0,
	PRIMARY KEY (`post`)
) DEFAULT CHARSET=utf8;

TRUNCATE TABLE `tp_subd`.`Forum`;
TRUNCATE TABLE `tp_subd`.`User`;
TRUNCATE TABLE `tp_subd`.`Post`;
TRUNCATE TABLE `tp_subd`.`Thread`;
TRUNCATE TABLE `tp_subd`.`Follower`;
TRUNCATE TABLE `tp_subd`.`Subscription`;


-----------
-- Other --
-----------
DROP TABLE Forum, Post, Subscription, Thread, User, Follower;

# Вопросы
# Что такое slug у Thread?
# Что такое points у Thread?