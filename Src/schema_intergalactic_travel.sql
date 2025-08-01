
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS intergalactic_travel;
USE intergalactic_travel;

-- Create table: planet
CREATE TABLE `planet` (
  `planet_id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) UNIQUE NOT NULL,
  `size` INT,
  `population` INT
);

-- Create table: spacestation
CREATE TABLE `spacestation` (
  `station_id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) UNIQUE NOT NULL,
  `location_type` VARCHAR(255),
  `planet_id` INT NOT NULL,
  `orbiting_planet_id` INT,
  FOREIGN KEY (`planet_id`) REFERENCES `planet` (`planet_id`),
  FOREIGN KEY (`orbiting_planet_id`) REFERENCES `planet` (`planet_id`)
);

-- Create table: spaceport
CREATE TABLE `spaceport` (
  `spaceport_id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `capacity_limit` INT,
  `fee_per_seat` INT,
  `planet_id` INT,
  `station_id` INT,
  FOREIGN KEY (`planet_id`) REFERENCES `planet` (`planet_id`),
  FOREIGN KEY (`station_id`) REFERENCES `spacestation` (`station_id`)
);

-- Create table: route
CREATE TABLE `route` (
  `route_id` INT PRIMARY KEY AUTO_INCREMENT,
  `origin_spaceport_id` INT NOT NULL,
  `destination_spaceport_id` INT NOT NULL,
  `distance` INT,
  FOREIGN KEY (`origin_spaceport_id`) REFERENCES `spaceport` (`spaceport_id`),
  FOREIGN KEY (`destination_spaceport_id`) REFERENCES `spaceport` (`spaceport_id`)
);

-- Create table: spacecraft_type
CREATE TABLE `spacecraft_type` (
  `craft_type_id` INT PRIMARY KEY AUTO_INCREMENT,
  `type_name` VARCHAR(255) UNIQUE NOT NULL,
  `capacity` INT,
  `range` INT
);

-- Create table: flight
CREATE TABLE `flight` (
  `flight_number` VARCHAR(255) PRIMARY KEY,
  `route_id` INT NOT NULL,
  `craft_type_id` INT NOT NULL,
  `departure_time` TIME,
  `flight_time` DECIMAL(5,2),
  FOREIGN KEY (`route_id`) REFERENCES `route` (`route_id`),
  FOREIGN KEY (`craft_type_id`) REFERENCES `spacecraft_type` (`craft_type_id`)
);

-- Create table: flight_schedule
CREATE TABLE `flight_schedule` (
  `flight_number` VARCHAR(255),
  `day_of_week` VARCHAR(255),
  PRIMARY KEY (`flight_number`, `day_of_week`),
  FOREIGN KEY (`flight_number`) REFERENCES `flight` (`flight_number`)
);
