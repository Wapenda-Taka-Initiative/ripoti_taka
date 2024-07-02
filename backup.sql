CREATE TABLE category (
	"categoryId" INT NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	description TEXT, 
	PRIMARY KEY ("categoryId")
);
CREATE TABLE reward (
	"rewardId" INT NOT NULL, 
	name VARCHAR(100), 
	"pointsRequired" INT, 
	PRIMARY KEY ("rewardId")
);
CREATE TABLE role (
	"roleId" INT NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	"default" BOOLEAN, 
	permissions INT, 
	PRIMARY KEY ("roleId")
);
CREATE TABLE status (
	"statusId" INT NOT NULL, 
	name VARCHAR(50), 
	PRIMARY KEY ("statusId")
);
CREATE TABLE user (
	"userId" INT NOT NULL, 
	"firstName" VARCHAR(30), 
	"middleName" VARCHAR(30), 
	"lastName" VARCHAR(30), 
	"userName" VARCHAR(50) NOT NULL, 
	"emailAddress" VARCHAR(100) NOT NULL, 
	"passwordHash" VARCHAR(100) NOT NULL, 
	"phoneNumber" VARCHAR(20), 
	gender VARCHAR(8) NOT NULL, 
	"locationAddress" VARCHAR(255), 
	about_me VARCHAR(140), 
	avatar_hash VARCHAR(32), 
	"pointsAcquired" INT, 
	last_seen DATETIME, 
	"dateCreated" DATETIME, 
	"lastUpdated" DATETIME, 
	"imageUrl" VARCHAR(200), 
	confirmed BOOLEAN, 
	active BOOLEAN, 
	"roleId" INT, 
	PRIMARY KEY ("userId"), 
	FOREIGN KEY("roleId") REFERENCES role ("roleId"), 
	UNIQUE ("userName")
);
CREATE TABLE report (
	"reportId" INT NOT NULL, 
	location VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL, 
	latitude FLOAT, 
	longitude FLOAT, 
	moderated BOOLEAN, 
	"isResolved" BOOLEAN, 
	"dateCreated" DATETIME, 
	"lastUpdated" DATETIME, 
	"categoryId" INT, 
	"userId" INT, 
	PRIMARY KEY ("reportId"), 
	FOREIGN KEY("categoryId") REFERENCES category ("categoryId"), 
	FOREIGN KEY("userId") REFERENCES user ("userId")
);
CREATE TABLE user_reward (
	"userRewardId" INT NOT NULL, 
	"userId" INT, 
	"rewardId" INT, 
	"dateAssigned" DATETIME, 
	"isAssigned" BOOLEAN, 
	PRIMARY KEY ("userRewardId"), 
	FOREIGN KEY("rewardId") REFERENCES reward ("rewardId"), 
	FOREIGN KEY("userId") REFERENCES user ("userId")
);
CREATE TABLE comment (
	"commentId" INT NOT NULL, 
	content TEXT, 
	"dateCreated" DATETIME, 
	"lastUpdated" DATETIME, 
	"reportId" INT, 
	PRIMARY KEY ("commentId"), 
	FOREIGN KEY("reportId") REFERENCES report ("reportId")
);
CREATE TABLE report_status (
	"reportStatusId" INT NOT NULL, 
	"reportId" INT, 
	"statusId" INT, 
	"dateCreated" DATETIME, 
	PRIMARY KEY ("reportStatusId"), 
	FOREIGN KEY("reportId") REFERENCES report ("reportId"), 
	FOREIGN KEY("statusId") REFERENCES status ("statusId")
);
