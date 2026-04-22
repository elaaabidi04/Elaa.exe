-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 22, 2026 at 11:31 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `portfolio_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `certifications`
--

CREATE TABLE `certifications` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `issuer` varchar(100) NOT NULL,
  `year` char(4) NOT NULL,
  `icon` varchar(10) DEFAULT '?',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `certifications`
--

INSERT INTO `certifications` (`id`, `name`, `issuer`, `year`, `icon`, `created_at`) VALUES
(1, 'Machine Learning Certificate', 'NVIDIA', '2026', '🏅', '2026-04-22 19:18:08'),
(2, 'Generative AI Certification', 'Go My Code', '2026', '✨', '2026-04-22 19:18:08');

-- --------------------------------------------------------

--
-- Table structure for table `projects`
--

CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `emoji` varchar(10) DEFAULT '✦',
  `description` text NOT NULL,
  `tags` varchar(300) DEFAULT '',
  `url` varchar(300) DEFAULT '',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` (`id`, `name`, `emoji`, `description`, `tags`, `url`, `created_at`) VALUES
(1, 'Wellness', '🌿', 'Full-stack web app for cancer patient excursion management using MVC architecture.', 'HTML,CSS,JS,PHP,MySQL,MVC', '', '2026-04-22 19:18:08'),
(2, 'Vaxera', '💉', 'Qt/C++ desktop app for vaccination centers with Arduino temperature monitoring and keypad access control.', 'C++,Qt,Arduino,Hardware', '', '2026-04-22 19:18:08'),
(3, 'SmartHeal', '🏥', 'Java desktop app + Symfony website for medical tourism covering the medical services module.', 'Java,Symfony,MySQL,MVC', '', '2026-04-22 19:18:08'),
(4, 'Elmo AI Chatbot', '🤖', 'Context-aware chatbot with conversation memory using SQLite. Full-stack AI integration with multi-turn dialogue.', 'Python,Flask,SQLite,NVIDIA API', 'https://github.com/elaaabidi04/Elmo', '2026-04-22 19:18:08'),
(5, 'Biblio-AI', '🎬', 'AI-powered movie & book recommender using NVIDIA LLaMA 4, TMDB and Open Library. Deployed on Render/Aiven.', 'Flask,MySQL,NVIDIA LLaMA 4,TMDB,Render', 'https://github.com/elaaabidi04/biblio-ai', '2026-04-22 19:18:08');

-- --------------------------------------------------------

--
-- Table structure for table `skills`
--

CREATE TABLE `skills` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `category` enum('language','framework','tool','other') DEFAULT 'other'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `skills`
--

INSERT INTO `skills` (`id`, `name`, `category`) VALUES
(1, 'HTML', 'language'),
(2, 'CSS', 'language'),
(3, 'JavaScript', 'language'),
(4, 'Python', 'language'),
(5, 'PHP', 'language'),
(6, 'Java', 'language'),
(7, 'C++', 'language'),
(8, 'C', 'language'),
(9, 'SQL', 'language'),
(10, 'Laravel', 'framework'),
(11, 'Symfony', 'framework'),
(12, 'Flask', 'framework'),
(13, 'Qt', 'framework'),
(14, 'Make', 'tool'),
(15, 'XAMPP', 'tool'),
(16, 'Arduino', 'tool');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `certifications`
--
ALTER TABLE `certifications`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `skills`
--
ALTER TABLE `skills`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `certifications`
--
ALTER TABLE `certifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `skills`
--
ALTER TABLE `skills`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
