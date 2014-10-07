CREATE TABLE IF NOT EXISTS 'tp_subd'.'Forum' (
	'user' VARCHAR(45) NOT NULL,
	'short_name' VARCHAR(45) NOT NULL,
	'name' VARCHAR(45) NOT NULL,
	'order' CHAR(4) NOT NULL,
	'limit' INT(11) NOT NULL,
	'forum' VARCHAR(45) NOT NULL,
	'since_id' INT(11) NOT NULL,
	'since' DATETIME NOT NULL,
	CONSTRAINT forum_name UNIQUE ('name', 'short_name')
);
#'related' /*TODO*/ NOT NULL DEFAULT /*TODO*/

CREATE TABLE IF NOT EXISTS 'tp_subd'.'Post' (
	'user' VARCHAR(45) NOT NULL,
	'order' CHAR(4) NOT NULL DEFAULT 'desc',
	'thread' INT(11) NOT NULL,
	'post' INT(11) NOT NULL AUTO_INCREMENT,
	'parent' INT(11) NULL DEFAULT NULL,
	'forum' VARCHAR(45) NOT NULL,
	'message' TEXT NOT NULL,
	'vote' CHAR(2) NOT NULL,
	'date' DATETIME NOT NULL,
	'since' DATETIME NOT NULL,
	#'related' /*TODO*/ NOT NULL DEFAULT /*TODO*/,
	'limit' INT(11) NOT NULL,
	'isSpam' BOOLEAN NOT NULL DEFAULT 'false',
	'isEdited' BOOLEAN NOT NULL DEFAULT 'false',
	'isDeleted' BOOLEAN NOT NULL DEFAULT 'false',
	'isHighlighted' BOOLEAN NOT NULL DEFAULT 'false',
	'isApproved' BOOLEAN NOT NULL DEFAULT 'false',
	PRIMARY KEY ('post')
);

CREATE TABLE IF NOT EXISTS 'tp_subd'.'User' (
	'since' DATETIME NOT NULL,
	'order' CHAR(4) NOT NULL DEFAULT 'desc',
	'user' VARCHAR(45) NOT NULL,
	'username' VARCHAR(45) NOT NULL,
	'follower' VARCHAR(45) NOT NULL,
	'wollowee' VARCHAR(45) NOT NULL,
	'name' VARCHAR(45) NOT NULL,
	'limit' INT(11) NOT NULL,
	'since_id' INT(11) NOT NULL,
	'email' VARCHAR(45) NOT NULL,
	'isAnonimus' BOOLEAN NOT NULL DEFAULT 'false',
	'about' TEXT NOT NULL,
	PRIMARY KEY ('email')
);

CREATE TABLE IF NOT EXISTS 'tp_subd'.'Thread' (
	'thread' INT(11) NOT NULL AUTO_INCREMENT,
	'isDeleted' BOOLEAN NOT NULL DEFAULT 'false',
	'isClosed' BOOLEAN NOT NULL DEFAULT 'false',
	'message' TEXT NOT NULL,
	'user' VARCHAR(45) NOT NULL,
	'date' DATETIME NOT NULL,
	'slug' VARCHAR(45) NOT NULL,
	'title' VARCHAR(45) NOT NULL,
	'limit' INT(11) NOT NULL,
	'forum' VARCHAR(45) NOT NULL,
	#'related' /*TODO*/ NOT NULL DEFAULT /*TODO*/,
	'since' DATETIME NOT NULL,
	'order' CHAR(4) NOT NULL DEFAULT 'desc',
	'vote' INT(2) NOT NULL
	PRIMARY KEY ('thread')
);

- типы
- дефолты
- инкременты
- начальные даты

TRUNCATE TABLE 'tp_subd'.'Forum';
TRUNCATE TABLE 'tp_subd'.'User';
TRUNCATE TABLE 'tp_subd'.'Post';
TRUNCATE TABLE 'tp_subd'.'Thread';
