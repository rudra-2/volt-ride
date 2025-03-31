-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 22, 2025 at 11:28 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `voltride`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin-id` int(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `mobile` double NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `station-id` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `charging_ports`
--

CREATE TABLE `charging_ports` (
  `port-id` int(255) NOT NULL,
  `station-id` int(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `vehicle-id` int(255) NOT NULL,
  `battery` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `charging_ports`
--

INSERT INTO `charging_ports` (`port-id`, `station-id`, `status`, `vehicle-id`, `battery`) VALUES
(1, 1, 'Available', 0, NULL),
(2, 1, 'Available', 0, NULL),
(3, 1, 'Occupied', 2, 45),
(4, 1, 'Available', 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `ride`
--

CREATE TABLE `ride` (
  `r-id` int(255) NOT NULL,
  `user-id` int(255) NOT NULL,
  `v-id` int(255) NOT NULL,
  `time` time NOT NULL,
  `date` date NOT NULL,
  `status` varchar(255) NOT NULL,
  `payment` decimal(10,0) NOT NULL,
  `profit` decimal(10,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ride`
--

INSERT INTO `ride` (`r-id`, `user-id`, `v-id`, `time`, `date`, `status`, `payment`, `profit`) VALUES
(1, 2, 1, '10:00:00', '2025-03-20', 'Completed', 100, 30),
(2, 2, 2, '12:30:00', '2025-03-21', 'Ongoing', 150, 50),
(3, 2, 1, '15:00:00', '2025-03-21', 'Pending', 80, 25);

-- --------------------------------------------------------

--
-- Table structure for table `stations`
--

CREATE TABLE `stations` (
  `station-id` int(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `master-id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stations`
--

INSERT INTO `stations` (`station-id`, `name`, `latitude`, `longitude`, `master-id`) VALUES
(1, 'PDEU', 50, 50, 1);

-- --------------------------------------------------------

--
-- Table structure for table `tracking`
--

CREATE TABLE `tracking` (
  `track_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `v_id` int(11) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tracking`
--

INSERT INTO `tracking` (`track_id`, `user_id`, `v_id`, `latitude`, `longitude`, `timestamp`) VALUES
(1, 2, 1, 50.1234, 50.5678, '2025-03-22 09:02:13'),
(2, 2, 2, 51.1234, 51.5678, '2025-03-22 09:02:13');

-- --------------------------------------------------------

--
-- Table structure for table `transaction`
--

CREATE TABLE `transaction` (
  `t-id` int(255) NOT NULL,
  `user-id` int(255) NOT NULL,
  `w-id` int(255) NOT NULL,
  `method` varchar(255) NOT NULL,
  `amount` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transaction`
--

INSERT INTO `transaction` (`t-id`, `user-id`, `w-id`, `method`, `amount`) VALUES
(1, 2, 1, 'Credit Card', 100),
(2, 2, 1, 'UPI', 150);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `user-id` int(255) NOT NULL,
  `role` varchar(10) NOT NULL DEFAULT 'user',
  `first-name` varchar(255) NOT NULL,
  `last-name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `mobile` double NOT NULL,
  `password` varchar(255) NOT NULL,
  `licence-photo` varchar(255) NOT NULL,
  `licence-number` varchar(255) NOT NULL,
  `approval` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user-id`, `role`, `first-name`, `last-name`, `email`, `mobile`, `password`, `licence-photo`, `licence-number`, `approval`) VALUES
(1, 'master', 'rm', 'patel', 'mhpatel2026@gmail.com', 8468788788, '000000', 'https://www.gstatic.com/mobilesdk/240501_mobilesdk/firebase_28dp.png', '11111111', 'pending'),
(2, 'user', 'acs', 'ascd', 'codergirgit@gmail.com', 987654321, '12345', 'Bombay.jpg', '213654', 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `vehicle`
--

CREATE TABLE `vehicle` (
  `v-id` int(255) NOT NULL,
  `reg-plate` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `battery` double NOT NULL,
  `station-id` int(255) NOT NULL,
  `status` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vehicle`
--

INSERT INTO `vehicle` (`v-id`, `reg-plate`, `name`, `battery`, `station-id`, `status`) VALUES
(2, 'GJ02CD5678', 'EV-Two', 51, 1, 'Occupied'),
(3, 'GJ03EF9101', 'EV-Three', 100, 1, 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `wallet`
--

CREATE TABLE `wallet` (
  `w-id` int(255) NOT NULL,
  `user-id` int(255) NOT NULL,
  `amount` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wallet`
--

INSERT INTO `wallet` (`w-id`, `user-id`, `amount`) VALUES
(1, 2, 250);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `charging_ports`
--
ALTER TABLE `charging_ports`
  ADD PRIMARY KEY (`port-id`);

--
-- Indexes for table `stations`
--
ALTER TABLE `stations`
  ADD PRIMARY KEY (`station-id`);

--
-- Indexes for table `tracking`
--
ALTER TABLE `tracking`
  ADD PRIMARY KEY (`track_id`);

--
-- Indexes for table `transaction`
--
ALTER TABLE `transaction`
  ADD PRIMARY KEY (`t-id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user-id`),
  ADD UNIQUE KEY `mobile` (`mobile`,`email`);

--
-- Indexes for table `vehicle`
--
ALTER TABLE `vehicle`
  ADD PRIMARY KEY (`v-id`);

--
-- Indexes for table `wallet`
--
ALTER TABLE `wallet`
  ADD PRIMARY KEY (`w-id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `charging_ports`
--
ALTER TABLE `charging_ports`
  MODIFY `port-id` int(255) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tracking`
--
ALTER TABLE `tracking`
  MODIFY `track_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `user-id` int(255) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `charging_ports`
--
ALTER TABLE `charging_ports`
  ADD CONSTRAINT `fk_station` FOREIGN KEY (`station-id`) REFERENCES `stations` (`station-id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
