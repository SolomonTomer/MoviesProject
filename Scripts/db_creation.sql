drop table movie_writers;
drop table movie_countries;
drop table movie_directors;
drop table movie_genres;
drop table movie_languages;
drop table movie_stars;
drop table movies;

CREATE TABLE `movie_writers` (
  `title` VARCHAR(200) NULL DEFAULT NULL,
  `writer` VARCHAR(250) NULL DEFAULT NULL
);
CREATE TABLE `movie_stars` (
  `title` VARCHAR(200) NULL DEFAULT NULL,
  `actor` VARCHAR(250) NULL DEFAULT NULL
);
CREATE TABLE `movie_languages` (
  `title` VARCHAR(200) NULL DEFAULT NULL,
  `language` VARCHAR(60) NULL DEFAULT NULL
);
CREATE TABLE `movie_genres` (
  `title` VARCHAR(200) NOT NULL,
  `genre` VARCHAR(50) NOT NULL
);
CREATE TABLE `movie_directors` (
  `title` VARCHAR(200) NULL DEFAULT NULL,
  `director` VARCHAR(250) NULL DEFAULT NULL
);
CREATE TABLE `movie_countries` (
  `title` VARCHAR(200) NULL DEFAULT NULL,
  `country` VARCHAR(200) NULL DEFAULT NULL
);
CREATE TABLE `movies` (
	`title` VARCHAR(200) NOT NULL,
	`release_date` DATE NOT NULL,
	`rated` VARCHAR(50) NULL DEFAULT NULL,
	`run_time` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,
	`budget` BIGINT(12) UNSIGNED NULL DEFAULT NULL,
	`opening_weekend` INT(12) UNSIGNED NULL DEFAULT NULL,
	`gross` INT(12) UNSIGNED NULL DEFAULT NULL,
	`imdb_score` FLOAT UNSIGNED NULL DEFAULT NULL,
	`meta_score` FLOAT UNSIGNED NULL DEFAULT NULL,
	`user_score` FLOAT UNSIGNED NULL DEFAULT NULL
);
CREATE TABLE `movie_tmp` (
  `title` VARCHAR(200) NULL DEFAULT NULL,
  `release_date` DATE NULL DEFAULT NULL,
  `run_time` INT(11) NULL DEFAULT NULL,
  `meta_score` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
  `user_score` FLOAT UNSIGNED NULL DEFAULT NULL,
  `genres` VARCHAR(500) NULL DEFAULT NULL
);

CREATE TABLE `persons` (
	`name` VARCHAR(250) NULL DEFAULT NULL,
	`meta_critic_highest` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
	`meta_critic_avg_career` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
	`meta_critic_lowest` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
	`meta_user_highest` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
	`meta_user_median` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
	`meta_user_lowest` TINYINT(3) UNSIGNED NULL DEFAULT NULL
);
