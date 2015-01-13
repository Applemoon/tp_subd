DROP TABLE Forum, Post, Subscription, Thread, User, Follower;

CREATE TABLE IF NOT EXISTS `User` (
	`user` INT NOT NULL AUTO_INCREMENT, -- user id
	`email` VARCHAR(45) NOT NULL, -- user email
	`name` VARCHAR(45) NULL, -- user name
	`username` VARCHAR(45) NULL, -- user name ???
	`isAnonymous` BOOLEAN NOT NULL DEFAULT 0,
	`about` TEXT NULL,
	PRIMARY KEY (`user`),
	UNIQUE KEY (`email`),
	UNIQUE KEY name_email (name, email)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Follower` (
	`follower` VARCHAR(45) NOT NULL, -- follower email
	`following` VARCHAR(45) NOT NULL -- following email
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Forum` (
	`forum` INT NOT NULL AUTO_INCREMENT, -- forum id
	`name` VARCHAR(45) NOT NULL, -- forum full name
	`short_name` VARCHAR(45) NOT NULL, -- forum short name
	`user` VARCHAR(45) NOT NULL, -- founder email
	PRIMARY KEY (`forum`),
	UNIQUE KEY (`name`), 
	UNIQUE KEY (`short_name`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Thread` (
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
	`points` INT NOT NULL DEFAULT 0,
	`posts` INT NOT NULL DEFAULT 0,
	PRIMARY KEY (`thread`),
	UNIQUE KEY (`title`),
	KEY (user)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Subscription` (
	`subscriber` VARCHAR(45) NOT NULL, -- subscriber email
	`thread` INT NOT NULL, -- thread id
	PRIMARY KEY (`subscriber`, `thread`)
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Post` (
	`post` INT NOT NULL AUTO_INCREMENT, -- post id
	`user` VARCHAR(45) NOT NULL, -- author email
	`thread` INT NOT NULL, -- thread id
	`forum` VARCHAR(45) NOT NULL, -- forum short_name
	`message` TEXT NOT NULL,
	`parent` INT NULL DEFAULT NULL, -- parent post id
	`date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`points` INT NOT NULL DEFAULT 0,
	`isSpam` BOOLEAN NOT NULL DEFAULT 0,
	`isEdited` BOOLEAN NOT NULL DEFAULT 0,
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isHighlighted` BOOLEAN NOT NULL DEFAULT 0,
	`isApproved` BOOLEAN NOT NULL DEFAULT 0,
	PRIMARY KEY (`post`),
	UNIQUE KEY `user_date` (`user`, `date`),
	KEY (`forum`),
	KEY `thread_date` (`thread`, `date`)
) DEFAULT CHARSET=utf8;

TRUNCATE TABLE `tp_subd`.`User`;
TRUNCATE TABLE `tp_subd`.`Follower`;
TRUNCATE TABLE `tp_subd`.`Forum`;
TRUNCATE TABLE `tp_subd`.`Thread`;
TRUNCATE TABLE `tp_subd`.`Subscription`;
TRUNCATE TABLE `tp_subd`.`Post`;

User
CREATE UNIQUE INDEX email ON User (email); -- используется, задан в CREATE TABLE
CREATE UNIQUE INDEX name_email ON User (name, email); -- используется, задан в CREATE TABLE
CREATE UNIQUE INDEX email_name ON User (email, name); -- ???

Follower
CREATE UNIQUE INDEX 'PRIMARY' ON Follower (follower, following); -- используется, задан в CREATE TABLE
CREATE UNIQUE INDEX fing_fer ON Follower (following, follower); -- ???

Forum
CREATE UNIQUE INDEX 'PRIMARY' ON Forum (forum); -- задан в CREATE TABLE
CREATE UNIQUE INDEX short_name ON Forum (short_name); -- используется, задан в CREATE TABLE

Thread
CREATE UNIQUE INDEX 'PRIMARY' ON Thread (thread); -- используется, задан в CREATE TABLE
CREATE UNIQUE INDEX title ON Thread (title); -- задан в CREATE TABLE, ???
CREATE INDEX forum ON Thread (forum); -- ???
CREATE INDEX user ON Thread (user); -- используется

Subscription
CREATE UNIQUE INDEX 'PRIMARY' ON Subscription (subscriber, thread); -- используется, задан в CREATE TABLE

Post
CREATE UNIQUE INDEX 'PRIMARY' ON Post (post); -- используется, задан в CREATE TABLE
CREATE UNIQUE INDEX user_date ON Post (user, date); -- ???, задан в CREATE TABLE
CREATE INDEX forum ON Post (forum); -- используется, задан в CREATE TABLE
CREATE INDEX user ON Post (user); -- ???
CREATE INDEX thread_date ON Post (thread, date); -- используется, задан в CREATE TABLE
CREATE INDEX user_date ON Post (user,date); -- используется, задан в CREATE TABLE
