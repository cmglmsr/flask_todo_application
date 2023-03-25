CREATE DATABASE IF NOT EXISTS cs353hw4db;
USE cs353hw4db;
CREATE TABLE User (id INT PRIMARY KEY, password VARCHAR(255), username VARCHAR(255), email VARCHAR(255));
CREATE TABLE Task (id INT PRIMARY KEY, title VARCHAR(255), description TEXT(255), status VARCHAR(255), deadline DATETIME, creation_time DATETIME, done_time DATETIME, user_id INT, task_type VARCHAR(255));
CREATE TABLE TaskType (type VARCHAR(255));