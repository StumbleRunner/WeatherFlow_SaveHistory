-- MySQL dump 10.13  Distrib 5.6.17, for Win64 (x86_64)
--
-- Host: localhost    Database: 
-- ------------------------------------------------------
-- Server version	5.6.17-log

--
-- Current Database: `weather`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `weather` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `weather`;

--
-- Table structure for table `airobs`
--

DROP TABLE IF EXISTS `airobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airobs` (
  `TimeStamp` bigint(20) NOT NULL,
  `Pressure` double NOT NULL,
  `AirTemp` double NOT NULL,
  `RelHumidty` double NOT NULL,
  `LightningCount` int(11) NOT NULL,
  `LightningLastDist` float NOT NULL,
  `Battery` float NOT NULL,
  `DeltaT` float NOT NULL,
  `DewPoint` float NOT NULL,
  `FeelsLike` float NOT NULL,
  `HeatIndex` float NOT NULL,
  `PressureTrend` float NOT NULL,
  `SeaLevelPressure` float NOT NULL,
  `VaporPressure` float NOT NULL,
  `WetBulbTemp` float NOT NULL,
  UNIQUE KEY `TimeStamp` (`TimeStamp`)
) ENGINE=InnoDB DEFAULT CHARSET=binary;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `skyobs`
--

DROP TABLE IF EXISTS `skyobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `skyobs` (
  `TimeStamp` bigint(20) NOT NULL,
  `Lux` bigint(20) NOT NULL,
  `UVindex` float NOT NULL,
  `PrecipAccum` float NOT NULL,
  `WindLull` float NOT NULL,
  `WindAvg` float NOT NULL,
  `WindGust` float NOT NULL,
  `WindDirection` float NOT NULL,
  `WindChill` float NOT NULL,
  `Battery` float NOT NULL,
  `RainRate` float NOT NULL,
  `SolarRadiation` double NOT NULL,
  UNIQUE KEY `TimeStamp` (`TimeStamp`)
) ENGINE=InnoDB DEFAULT CHARSET=binary;
/*!40101 SET character_set_client = @saved_cs_client */;

USE `weather`;

