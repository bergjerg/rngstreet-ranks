/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.26-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: rngstreet
-- ------------------------------------------------------
-- Server version	10.5.26-MariaDB-0+deb11u2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `discord_rankup_request`
--

DROP TABLE IF EXISTS `discord_rankup_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discord_rankup_request` (
  `wom_id` int(11) DEFAULT NULL,
  `request_timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ehb_cfg`
--

DROP TABLE IF EXISTS `ehb_cfg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ehb_cfg` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) NOT NULL,
  `KILLS` int(11) DEFAULT 0,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `main_rsn_map`
--

DROP TABLE IF EXISTS `main_rsn_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_rsn_map` (
  `DISCORD_ID` varchar(255) NOT NULL,
  `WOM_ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`DISCORD_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `member_points`
--

DROP TABLE IF EXISTS `member_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `member_points` (
  `SNAPSHOT_TIMESTAMP` datetime DEFAULT current_timestamp(),
  `MONTH` int(11) NOT NULL,
  `WOM_ID` int(11) NOT NULL,
  `RSN` varchar(255) NOT NULL,
  `XP_POINTS` decimal(4,1) DEFAULT 0.0,
  `EHB_POINTS` decimal(4,1) DEFAULT 0.0,
  `EVENT_POINTS` decimal(4,1) DEFAULT 0.0,
  `SPLIT_POINTS` decimal(4,1) DEFAULT 0.0,
  `TIME_POINTS` decimal(4,1) DEFAULT 0.0,
  PRIMARY KEY (`MONTH`,`WOM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `member_points_archived`
--

DROP TABLE IF EXISTS `member_points_archived`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `member_points_archived` (
  `SNAPSHOT_TIMESTAMP` datetime DEFAULT current_timestamp(),
  `MONTH` int(11) NOT NULL,
  `WOM_ID` int(11) NOT NULL,
  `RSN` varchar(255) NOT NULL,
  `XP_POINTS` decimal(4,1) DEFAULT 0.0,
  `EHB_POINTS` decimal(4,1) DEFAULT 0.0,
  `EVENT_POINTS` decimal(4,1) DEFAULT 0.0,
  `SPLIT_POINTS` decimal(4,1) DEFAULT 0.0,
  `TIME_POINTS` decimal(4,1) DEFAULT 0.0,
  PRIMARY KEY (`MONTH`,`WOM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `member_points_bkp`
--

DROP TABLE IF EXISTS `member_points_bkp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `member_points_bkp` (
  `SNAPSHOT_TIMESTAMP` datetime DEFAULT current_timestamp(),
  `MONTH` int(11) NOT NULL,
  `WOM_ID` int(11) NOT NULL,
  `RSN` varchar(255) NOT NULL,
  `XP_POINTS` decimal(4,1) DEFAULT 0.0,
  `EHB_POINTS` decimal(4,1) DEFAULT 0.0,
  `EVENT_POINTS` decimal(4,1) DEFAULT 0.0,
  `SPLIT_POINTS` decimal(4,1) DEFAULT 0.0,
  `TIME_POINTS` decimal(4,1) DEFAULT 0.0,
  PRIMARY KEY (`MONTH`,`WOM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `members` (
  `WOM_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) DEFAULT NULL,
  `MAIN_WOM_ID` int(11) DEFAULT NULL,
  `JOIN_DATE` date DEFAULT NULL,
  `RANK` varchar(255) DEFAULT NULL,
  `POINTS` decimal(4,1) DEFAULT 0.0,
  `WOM_RANK` varchar(255) DEFAULT NULL,
  `DISCORD_ID` varchar(255) DEFAULT NULL,
  `ACCOUNT_TYPE` varchar(255) DEFAULT 'REGULAR',
  `RSN` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`WOM_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2063571 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `members_archived`
--

DROP TABLE IF EXISTS `members_archived`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `members_archived` (
  `WOM_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) DEFAULT NULL,
  `MAIN_WOM_ID` int(11) DEFAULT NULL,
  `JOIN_DATE` date DEFAULT NULL,
  `RANK` varchar(255) DEFAULT NULL,
  `POINTS` decimal(4,1) DEFAULT 0.0,
  `WOM_RANK` varchar(255) DEFAULT NULL,
  `DISCORD_ID` varchar(255) DEFAULT NULL,
  `ACCOUNT_TYPE` varchar(255) DEFAULT 'REGULAR',
  `RSN` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`WOM_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1130820 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `members_bkp`
--

DROP TABLE IF EXISTS `members_bkp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `members_bkp` (
  `WOM_ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) DEFAULT NULL,
  `MAIN_WOM_ID` int(11) DEFAULT NULL,
  `JOIN_DATE` date DEFAULT NULL,
  `RANK` varchar(255) DEFAULT NULL,
  `POINTS` decimal(4,1) DEFAULT 0.0,
  `WOM_RANK` varchar(255) DEFAULT NULL,
  `DISCORD_ID` varchar(255) DEFAULT NULL,
  `ACCOUNT_TYPE` varchar(255) DEFAULT 'REGULAR',
  `RSN` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`WOM_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2040041 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `points_cfg`
--

DROP TABLE IF EXISTS `points_cfg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `points_cfg` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `CODE` varchar(255) NOT NULL,
  `NAME` varchar(255) NOT NULL,
  `VALUE` decimal(3,1) DEFAULT 0.0,
  `MONTHLY_LIMIT` int(11) DEFAULT 20,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `processed_discord_reactions`
--

DROP TABLE IF EXISTS `processed_discord_reactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `processed_discord_reactions` (
  `message_id` bigint(20) NOT NULL,
  PRIMARY KEY (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rank_cfg`
--

DROP TABLE IF EXISTS `rank_cfg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rank_cfg` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  `POINTS` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stg_discord_new_rsn`
--

DROP TABLE IF EXISTS `stg_discord_new_rsn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stg_discord_new_rsn` (
  `rsn` varchar(255) NOT NULL,
  `discord_id` varchar(255) DEFAULT NULL,
  `unload_time` datetime DEFAULT NULL,
  PRIMARY KEY (`rsn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stg_gained`
--

DROP TABLE IF EXISTS `stg_gained`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stg_gained` (
  `UNLOAD_TIME` datetime DEFAULT current_timestamp(),
  `WOM_ID` int(11) DEFAULT NULL,
  `MONTH` int(11) DEFAULT NULL,
  `RSN` varchar(255) DEFAULT NULL,
  `METRIC` varchar(255) DEFAULT NULL,
  `GAINED` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stg_members`
--

DROP TABLE IF EXISTS `stg_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stg_members` (
  `WOM_ID` int(11) NOT NULL,
  `RSN` varchar(100) DEFAULT NULL,
  `WOM_RANK` varchar(50) DEFAULT NULL,
  `ACCOUNT_TYPE` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`WOM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `vw_discord_mod_rank_mismatch`
--

DROP TABLE IF EXISTS `vw_discord_mod_rank_mismatch`;
/*!50001 DROP VIEW IF EXISTS `vw_discord_mod_rank_mismatch`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_discord_mod_rank_mismatch` AS SELECT
 1 AS `discord_id`,
  1 AS `rsn`,
  1 AS `rank`,
  1 AS `wom_rank` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_discord_rank_check`
--

DROP TABLE IF EXISTS `vw_discord_rank_check`;
/*!50001 DROP VIEW IF EXISTS `vw_discord_rank_check`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_discord_rank_check` AS SELECT
 1 AS `DISCORD_ID`,
  1 AS `WOM_ID`,
  1 AS `RSN`,
  1 AS `POINTS`,
  1 AS `current_rank`,
  1 AS `wom_rank`,
  1 AS `current_rank_points`,
  1 AS `next_rank_points`,
  1 AS `next_rank`,
  1 AS `XP_POINTS`,
  1 AS `EHB_POINTS`,
  1 AS `SPLIT_POINTS`,
  1 AS `EVENT_POINTS`,
  1 AS `month_total_points`,
  1 AS `prev_XP_POINTS`,
  1 AS `prev_EHB_POINTS`,
  1 AS `prev_SPLIT_POINTS`,
  1 AS `prev_EVENT_POINTS`,
  1 AS `prev_month_total_points` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_max_rank_discord`
--

DROP TABLE IF EXISTS `vw_max_rank_discord`;
/*!50001 DROP VIEW IF EXISTS `vw_max_rank_discord`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_max_rank_discord` AS SELECT
 1 AS `discord_id`,
  1 AS `deserved_rank` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_member_points`
--

DROP TABLE IF EXISTS `vw_member_points`;
/*!50001 DROP VIEW IF EXISTS `vw_member_points`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_member_points` AS SELECT
 1 AS `SNAPSHOT_TIMESTAMP`,
  1 AS `MONTH`,
  1 AS `WOM_ID`,
  1 AS `RSN`,
  1 AS `XP_POINTS`,
  1 AS `EHB_POINTS`,
  1 AS `EVENT_POINTS`,
  1 AS `SPLIT_POINTS`,
  1 AS `TIME_POINTS` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_member_rankups`
--

DROP TABLE IF EXISTS `vw_member_rankups`;
/*!50001 DROP VIEW IF EXISTS `vw_member_rankups`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_member_rankups` AS SELECT
 1 AS `WOM_ID`,
  1 AS `NAME`,
  1 AS `MAIN_WOM_ID`,
  1 AS `JOIN_DATE`,
  1 AS `RANK`,
  1 AS `POINTS`,
  1 AS `WOM_RANK`,
  1 AS `DISCORD_ID`,
  1 AS `ACCOUNT_TYPE`,
  1 AS `RSN`,
  1 AS `CURRENT_RANK_POINTS`,
  1 AS `NEXT_RANK_POINTS`,
  1 AS `NEXT_RANK` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_total_points`
--

DROP TABLE IF EXISTS `vw_total_points`;
/*!50001 DROP VIEW IF EXISTS `vw_total_points`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_total_points` AS SELECT
 1 AS `WOM_ID`,
  1 AS `TOTAL_POINTS` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_web_homepage`
--

DROP TABLE IF EXISTS `vw_web_homepage`;
/*!50001 DROP VIEW IF EXISTS `vw_web_homepage`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_web_homepage` AS SELECT
 1 AS `WOM_ID`,
  1 AS `NAME`,
  1 AS `MAIN_WOM_ID`,
  1 AS `JOIN_DATE`,
  1 AS `RANK`,
  1 AS `POINTS`,
  1 AS `WOM_RANK`,
  1 AS `DISCORD_ID`,
  1 AS `ACCOUNT_TYPE`,
  1 AS `RSN`,
  1 AS `NEXT_RANK`,
  1 AS `current_rank_points`,
  1 AS `last_active` */;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vw_discord_mod_rank_mismatch`
--

/*!50001 DROP VIEW IF EXISTS `vw_discord_mod_rank_mismatch`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_discord_mod_rank_mismatch` AS select `m`.`DISCORD_ID` AS `discord_id`,`m`.`RSN` AS `rsn`,`m`.`RANK` AS `rank`,`m`.`WOM_RANK` AS `wom_rank` from ((`members` `m` join `rank_cfg` `r_current` on(`r_current`.`NAME` = `m`.`RANK`)) join `rank_cfg` `r_wom` on(`r_wom`.`NAME` = `m`.`WOM_RANK`)) where `r_current`.`POINTS` is not null and `r_wom`.`POINTS` is not null and `r_wom`.`POINTS` < `r_current`.`POINTS` and `m`.`RSN` is not null order by `m`.`RSN` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_discord_rank_check`
--

/*!50001 DROP VIEW IF EXISTS `vw_discord_rank_check`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_discord_rank_check` AS select `m`.`DISCORD_ID` AS `DISCORD_ID`,`m`.`WOM_ID` AS `WOM_ID`,`m`.`RSN` AS `RSN`,`m`.`POINTS` AS `POINTS`,`m`.`RANK` AS `current_rank`,`m`.`WOM_RANK` AS `wom_rank`,`rc_current`.`POINTS` AS `current_rank_points`,`rc_next`.`POINTS` AS `next_rank_points`,`rc_next`.`NAME` AS `next_rank`,`mp`.`XP_POINTS` AS `XP_POINTS`,`mp`.`EHB_POINTS` AS `EHB_POINTS`,`mp`.`SPLIT_POINTS` AS `SPLIT_POINTS`,`mp`.`EVENT_POINTS` AS `EVENT_POINTS`,`mp`.`XP_POINTS` + `mp`.`EHB_POINTS` + `mp`.`EVENT_POINTS` + `mp`.`SPLIT_POINTS` AS `month_total_points`,`mp_prev`.`XP_POINTS` AS `prev_XP_POINTS`,`mp_prev`.`EHB_POINTS` AS `prev_EHB_POINTS`,`mp_prev`.`SPLIT_POINTS` AS `prev_SPLIT_POINTS`,`mp_prev`.`EVENT_POINTS` AS `prev_EVENT_POINTS`,`mp_prev`.`XP_POINTS` + `mp_prev`.`EHB_POINTS` + `mp_prev`.`EVENT_POINTS` + `mp_prev`.`SPLIT_POINTS` AS `prev_month_total_points` from ((((`members` `m` left join `rank_cfg` `rc_current` on(`rc_current`.`NAME` collate utf8mb4_general_ci = `m`.`RANK`)) left join `rank_cfg` `rc_next` on(`rc_next`.`POINTS` = (select min(`rank_cfg`.`POINTS`) from `rank_cfg` where `rank_cfg`.`POINTS` > ifnull(`rc_current`.`POINTS`,9999)))) left join `member_points` `mp` on(`mp`.`WOM_ID` = `m`.`WOM_ID` and `mp`.`MONTH` = date_format(curdate(),'%Y%m'))) left join `member_points` `mp_prev` on(`mp_prev`.`WOM_ID` = `m`.`WOM_ID` and `mp_prev`.`MONTH` = date_format(curdate() - interval 1 month,'%Y%m'))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_max_rank_discord`
--

/*!50001 DROP VIEW IF EXISTS `vw_max_rank_discord`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_max_rank_discord` AS select `ranked`.`discord_id` AS `discord_id`,`ranked`.`deserved_rank` AS `deserved_rank` from (select `m`.`DISCORD_ID` AS `discord_id`,`rc`.`NAME` AS `deserved_rank`,`rc`.`POINTS` AS `POINTS`,row_number() over ( partition by `m`.`DISCORD_ID` order by coalesce(`rc`.`POINTS`,9999) desc) AS `rn` from (`members` `m` join `rank_cfg` `rc` on(`m`.`RANK` = `rc`.`NAME`)) where `m`.`DISCORD_ID` <> '') `ranked` where `ranked`.`rn` = 1 and `ranked`.`POINTS` is not null */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_member_points`
--

/*!50001 DROP VIEW IF EXISTS `vw_member_points`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_member_points` AS with member_list as (select distinct current_timestamp() AS `SNAPSHOT_TIMESTAMP`,`g`.`MONTH` AS `MONTH`,`g`.`WOM_ID` AS `WOM_ID`,`g`.`RSN` AS `RSN` from `stg_gained` `g`), ehp as (select `g`.`MONTH` AS `MONTH`,`g`.`WOM_ID` AS `WOM_ID`,least(`g`.`GAINED` / `cfg`.`VALUE`,`cfg`.`MONTHLY_LIMIT`) AS `POINTS` from (`stg_gained` `g` join `points_cfg` `cfg` on(`g`.`METRIC` = `cfg`.`CODE`)) where `g`.`METRIC` = 'EHP'), ehb as (select `g`.`MONTH` AS `MONTH`,`g`.`WOM_ID` AS `WOM_ID`,least(`g`.`GAINED` / `cfg`.`VALUE`,`cfg`.`MONTHLY_LIMIT`) AS `POINTS` from (`stg_gained` `g` join `points_cfg` `cfg` on(`g`.`METRIC` = `cfg`.`CODE`)) where `g`.`METRIC` = 'EHB')select `m`.`SNAPSHOT_TIMESTAMP` AS `SNAPSHOT_TIMESTAMP`,`m`.`MONTH` AS `MONTH`,`m`.`WOM_ID` AS `WOM_ID`,`m`.`RSN` AS `RSN`,coalesce(`ehp`.`POINTS`,0) AS `XP_POINTS`,coalesce(`ehb`.`POINTS`,0) AS `EHB_POINTS`,0 AS `EVENT_POINTS`,0 AS `SPLIT_POINTS`,0 AS `TIME_POINTS` from ((`member_list` `m` left join `ehp` on(`m`.`WOM_ID` = `ehp`.`WOM_ID` and `m`.`MONTH` = `ehp`.`MONTH`)) left join `ehb` on(`m`.`WOM_ID` = `ehb`.`WOM_ID` and `m`.`MONTH` = `ehb`.`MONTH`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_member_rankups`
--

/*!50001 DROP VIEW IF EXISTS `vw_member_rankups`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_member_rankups` AS select `m`.`WOM_ID` AS `WOM_ID`,`m`.`NAME` AS `NAME`,`m`.`MAIN_WOM_ID` AS `MAIN_WOM_ID`,`m`.`JOIN_DATE` AS `JOIN_DATE`,`m`.`RANK` AS `RANK`,`m`.`POINTS` AS `POINTS`,`m`.`WOM_RANK` AS `WOM_RANK`,`m`.`DISCORD_ID` AS `DISCORD_ID`,`m`.`ACCOUNT_TYPE` AS `ACCOUNT_TYPE`,`m`.`RSN` AS `RSN`,`rc`.`POINTS` AS `CURRENT_RANK_POINTS`,`next_rc`.`POINTS` AS `NEXT_RANK_POINTS`,`next_rc`.`NAME` AS `NEXT_RANK` from ((`members` `m` left join `rank_cfg` `rc` on(`rc`.`NAME` collate utf8mb4_general_ci = `m`.`RANK` collate utf8mb4_general_ci)) left join `rank_cfg` `next_rc` on(`next_rc`.`POINTS` = (select min(`r2`.`POINTS`) from `rank_cfg` `r2` where `r2`.`POINTS` > `rc`.`POINTS`))) where `m`.`POINTS` >= ifnull(`next_rc`.`POINTS`,0) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_total_points`
--

/*!50001 DROP VIEW IF EXISTS `vw_total_points`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_total_points` AS select `mp`.`WOM_ID` AS `WOM_ID`,sum(`mp`.`XP_POINTS` + `mp`.`EHB_POINTS` + `mp`.`EVENT_POINTS` + `mp`.`SPLIT_POINTS` + `mp`.`TIME_POINTS`) AS `TOTAL_POINTS` from `member_points` `mp` group by `mp`.`WOM_ID` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_web_homepage`
--

/*!50001 DROP VIEW IF EXISTS `vw_web_homepage`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_web_homepage` AS select `m`.`WOM_ID` AS `WOM_ID`,`m`.`NAME` AS `NAME`,if(`mrm`.`WOM_ID` is not null and `mrm`.`WOM_ID` <> `m`.`WOM_ID`,`mrm`.`WOM_ID`,0) AS `MAIN_WOM_ID`,`m`.`JOIN_DATE` AS `JOIN_DATE`,case when `m`.`RANK` = 'Achiever' then `m`.`RANK` when `rc`.`POINTS` is null then 'Moderator' else `m`.`RANK` end AS `RANK`,`m`.`POINTS` AS `POINTS`,case when `m`.`WOM_RANK` is null then 'Not In Clan' when `m`.`WOM_RANK` <> `m`.`RANK` then `m`.`WOM_RANK` else '' end AS `WOM_RANK`,`m`.`DISCORD_ID` AS `DISCORD_ID`,`m`.`ACCOUNT_TYPE` AS `ACCOUNT_TYPE`,`m`.`RSN` AS `RSN`,ifnull((select `rc2`.`NAME` from `rank_cfg` `rc2` where `rc2`.`POINTS` > (select `rc1`.`POINTS` from `rank_cfg` `rc1` where `rc1`.`NAME` = `m`.`RANK`) and `m`.`POINTS` >= `rc2`.`POINTS` order by `rc2`.`POINTS` limit 1),'') AS `NEXT_RANK`,`rc`.`POINTS` AS `current_rank_points`,case when `lap`.`months_since_active` = 1 then 'Last Month' when `lap`.`months_since_active` > 1 then concat(`lap`.`months_since_active`,' Months Ago') else '' end AS `last_active` from (((`members` `m` left join `main_rsn_map` `mrm` on(`m`.`DISCORD_ID` = `mrm`.`DISCORD_ID`)) left join `rank_cfg` `rc` on(`m`.`RANK` = `rc`.`NAME`)) left join (select `mp`.`WOM_ID` AS `WOM_ID`,floor(extract(year from curdate()) * 12 + extract(month from curdate())) - floor(max(`mp`.`MONTH`) / 100) * 12 - max(`mp`.`MONTH`) MOD 100 AS `months_since_active` from `member_points` `mp` where `mp`.`XP_POINTS` + `mp`.`EHB_POINTS` > 0 group by `mp`.`WOM_ID`) `lap` on(`m`.`WOM_ID` = `lap`.`WOM_ID`)) order by `rc`.`POINTS` desc,`m`.`POINTS` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-21 20:50:42
