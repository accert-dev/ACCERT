CREATE DATABASE  IF NOT EXISTS `accert_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `accert_db`;
-- MySQL dump 10.13  Distrib 8.0.38, for macos14 (arm64)
--
-- Host: 127.0.0.1    Database: accert_db
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mirror_acco`
--

DROP TABLE IF EXISTS `mirror_acco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
/*CREATE TABLE `mirror_acco` (
  `ind` int DEFAULT NULL,
  `code_of_account` varchar(20) NOT NULL,
  `account_description` text,
  `total_cost` double DEFAULT NULL,
  `level` int DEFAULT NULL,
  `supaccount` text,
  `review_status` text,
  `prn` double DEFAULT NULL,
  `alg_name` text,
  `fun_unit` text,
  `variables` text,
  PRIMARY KEY (`code_of_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; */

CREATE TABLE `mirror_acco` (
  `ind` int DEFAULT NULL,
  `code_of_account` varchar(20) NOT NULL,
  `account_description` text,
  `total_cost` double DEFAULT NULL,
  `total_cost_dollars` double DEFAULT NULL,
  `level` int DEFAULT NULL,
  `prn` double DEFAULT NULL,
  `supaccount` text,
  `alg_name` text,
  `fun_unit` text,
  `variables` text,
  `algno` text, 
  PRIMARY KEY (`code_of_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mirror_acco`
--

LOCK TABLES `mirror_acco` WRITE;
/*!40000 ALTER TABLE `mirror_acco` DISABLE KEYS */;
INSERT INTO `mirror_acco` VALUES (1, '10', 'Pre-Construction_Costs', '24.18611754', '$24186117.540000003', '0', '0.0046878318104200244', '', 'ac10', 'million', '', ''), (2, '11', 'Land_and_Land_Rights', '1.18611754', '$1186117.5399999998', '1', '0.00022989715177366762', '1', 'ac11', 'million', '', ''), (3, '12', 'Site_Permits', '10.0', '$10000000.0', '1', '0.0019382324602810245', '1', 'ac12', 'million', '', ''), (4, '13', 'Plant_Licensing', '0.0', '$0.0', '1', '0.0', '1', 'ac13', 'million', '', ''), (5, '14', 'Plant_Permits', '5.0', '$5000000.0', '1', '0.0009691162301405122', '1', 'ac14', 'million', '', ''), (6, '15', 'Plant_Studies', '5.0', '$5000000.0', '1', '0.0009691162301405122', '1', 'ac15', 'million', '', ''), (7, '16', 'Plant_Reports', '2.0', '$2000000.0', '1', '0.00038764649205620487', '1', 'ac16', 'million', '', ''), (8, '17', 'Other_Pre-Construction_Costs', '1.0', '$1000000.0', '1', '0.00019382324602810244', '1', 'ac17', 'million', '', ''), (9, '19', 'Contingency_on_Pre-Construction_Costs', '0.0', '$0.0', '1', '0.0', '1', 'ac19', 'million', '', ''), (10, '20', 'Capitalized_Direct_Costs_(CDC)', '1298.175963', '$1298175963.0', '0', '0.2516166790643178', '', 'ac20', 'million', '', ''), (11, '21', 'Structures_and_Improvements', '112.9457941', '$112945794.1', '1', '0.021891520437683703', '2', 'ac21', 'million', '', ''), (12, '21.1', 'Site_Preparation/Yard_Work', '42.37641442', '$42376414.42', '2', '0.008213534197916489', '21', 'ac21.1', 'million', '', ''), (13, '21.2', 'Heat_Island_Building', '29.53699334', '$29536993.34', '2', '0.005724955927069243', '21', 'ac21.2', 'million', '', ''), (14, '21.3', 'Turbine_Generator_Building', '8.538531265', '$8538531.264999999', '2', '0.0016549658460947396', '21', 'ac21.3', 'million', '', ''), (15, '21.4', 'Heat_Exchanger_Building', '5.976971885', '$5976971.885', '2', '0.0011584760921694063', '21', 'ac21.4', 'million', '', ''), (16, '21.5', 'Power_Supply_and_Energy_Storage', '1.707706253', '$1707706.253', '2', '0.00033099316921894796', '21', 'ac21.5', 'million', '', ''), (17, '21.6', 'Reactor_Auxiliaries', '0.8538531265', '$853853.1265', '2', '0.00016549658460947398', '21', 'ac21.6', 'million', '', ''), (18, '21.7', 'Hot_Cell', '14.76849667', '$14768496.67', '2', '0.0028624779635346214', '21', 'ac21.7', 'million', '', ''), (19, '21.8', 'Reactor_Services', '2.956861753', '$2956861.753', '2', '0.0005731085430228053', '21', 'ac21.8', 'million', '', ''), (20, '21.9', 'Service_Water', '0.0474362848', '$47436.2848', '2', '9.194254699449537e-06', '21', 'ac21.9', 'million', '', ''), (21, '21.10', 'Fuel_Storage', '0.1739330443', '$173933.0443', '2', '3.3712267237775744e-05', '', 'ac21.10', 'million', '', ''), (22, '21.11', 'Control_Room', '0.1423088544', '$142308.85439999998', '2', '2.7582764098348607e-05', '211', 'ac21.11', 'million', '', ''), (23, '21.12', 'Onsite_AC_Power', '0.1264967595', '$126496.7595', '2', '2.4518012538326203e-05', '211', 'ac21.12', 'million', '', ''), (24, '21.13', 'Administration', '0.6957321771', '$695732.1771', '2', '0.00013484906893172064', '211', 'ac21.13', 'million', '', ''), (25, '21.14', 'Site_Services', '0.252993519', '$252993.519', '2', '4.903602507665241e-05', '211', 'ac21.14', 'million', '', ''), (26, '21.15', 'Cryogenics', '0.3794902784', '$379490.2784', '2', '7.35540375955963e-05', '211', 'ac21.15', 'million', '', ''), (27, '21.16', 'Security', '0.1423088544', '$142308.85439999998', '2', '2.7582764098348607e-05', '211', 'ac21.16', 'million', '', ''), (28, '21.17', 'Ventilation_Stack', '4.269265632', '$4269265.632', '2', '0.0008274829229504582', '211', 'ac21.17', 'million', '', ''), (29, '22', 'Heat_Island_Plant_Equipment', '1111.99892', '$1111998920.0', '1', '0.21553124025414422', '2', 'ac22', 'million', '', ''), (30, '22.1', 'Heat_Island_Components', '901.9675668', '$901967566.8', '2', '0.17482228160924532', '22', 'ac22.1', 'million', '', ''), (31, '22.1.1', 'First_Wall_and_Blanket', '43.19343421', '$43193434.21', '3', '0.008371891625683487', '221', 'ac22.1.1', 'million', '', ''), (32, '22.1.2', 'Magnet_Radiation_Shield', '94.73695574', '$94736955.74', '3', '0.01836222428034747', '221', 'ac22.1.2', 'million', '', ''), (33, '22.1.3', 'Coils', '272.0399768', '$272039976.79999995', '3', '0.05272767135278568', '221', 'ac22.1.3', 'million', '', ''), (34, '22.1.3.1', 'HF_Coils', '116.4', '$116400000.0', '4', '0.022561025837671125', '2213', 'ac22.1.3.1', 'million', '', ''), (35, '22.1.3.2', 'LF_Coils', '12.50524', '$12505240.0', '4', '0.0024238062091604677', '2213', 'ac22.1.3.2', 'million', '', ''), (36, '22.1.3.3', 'CC_Coils', '143.1347368', '$143134736.8', '4', '0.02774283930595409', '2213', 'ac22.1.3.3', 'million', '', ''), (37, '22.1.4', 'Supplemental_Heating', '227.453', '$227453000.0', '3', '0.04408567877882998', '221', 'ac22.1.4', 'million', '', ''), (38, '22.1.4.1', 'NBI', '105.963', '$105963000.0', '4', '0.02053809261887582', '2214', 'ac22.1.4.1', 'million', '', ''), (39, '22.1.4.2', 'ICRH', '41.49', '$41490000.0', '4', '0.008041726477705971', '2214', 'ac22.1.4.2', 'million', '', ''), (40, '22.1.4.3', 'ECH', '80.0', '$80000000.0', '4', '0.015505859682248196', '2214', 'ac22.1.4.3', 'million', '', ''), (41, '22.1.5', 'Primary_Structure_and_Support', '0.0', '$0.0', '3', '0.0', '221', 'ac22.1.5', 'million', '', ''), (42, '22.1.6', 'Vacuum_System', '2.031827257', '$2031827.2570000002', '3', '0.00039381535432011556', '221', 'ac22.1.6', 'million', '', ''), (43, '22.1.6.2', 'Vessel_Refrigerators', '0.0', '$0.0', '4', '0.0', '2216', 'ac22.1.6.2', 'million', '', ''), (44, '22.1.6.3', 'Primary_Vacuum_Pumps', '1.689827257', '$1689827.257', '4', '0.0003275278041785045', '2216', 'ac22.1.6.3', 'million', '', ''), (45, '22.1.6.4', 'Backing_Vacuum_Pumps', '0.342', '$342000.0', '4', '6.628755014161104e-05', '2216', 'ac22.1.6.4', 'million', '', ''), (46, '22.1.7', 'Power_Supplies', '0.0', '$0.0', '3', '0.0', '221', 'ac22.1.7', 'million', '', ''), (47, '22.1.8', 'Divertor', '0.0', '$0.0', '3', '0.0', '221', 'ac22.1.8', 'million', '', ''), (48, '22.1.9', 'Direct_Energy_Convertor', '109.3171648', '$109317164.8', '3', '0.02118820772812502', '221', 'ac22.1.9', 'million', '', ''), (49, '22.1.11', 'Assembly_and_Installation_Costs', '153.1952079', '$153195207.9', '3', '0.029692792471128007', '2211', 'ac22.1.11', 'million', '', ''), (50, '22.2', 'Main_and_Secondary_Coolant', '33.6494515', '$33649451.5', '2', '0.0065220459167952', '22', 'ac22.2', 'million', '', ''), (51, '22.3', 'Auxiliary_Cooling_Systems', '0.3521982635', '$352198.2635', '2', '6.826421067703095e-05', '22', 'ac22.3', 'million', '', ''), (52, '22.4', 'Radioactive_Waste_Treatment', '0.6275532695', '$627553.2695', '2', '0.00012163441175003857', '22', 'ac22.4', 'million', '', ''), (53, '22.5', 'Fuel_Handling_and_Storage', '88.65405229', '$88654052.28999999', '2', '0.017183216188392927', '22', 'ac22.5', 'million', '', ''), (54, '22.6', 'Other_Heat_Island_Equipment', '1.748097852', '$1748097.852', '2', '0.0003388220000493934', '22', 'ac22.6', 'million', '', ''), (55, '22.7', 'Instrumentation_and_Control', '85.0', '$85000000.0', '2', '0.01647497591238871', '22', 'ac22.7', 'million', '', ''), (56, '23', 'Turbine_Plant_Equipment', '39.82276109', '$39822761.09', '1', '0.007718576820265415', '2', 'ac23', 'million', '', ''), (57, '24', 'Electric_Plant_Equipment', '9.819310954', '$9819310.954', '1', '0.0019032107228635835', '2', 'ac24', 'million', '', ''), (58, '25', 'Miscellaneous_Plant_Equipment', '6.909885486', '$6909885.4860000005', '1', '0.0013392964345789922', '2', 'ac25', 'million', '', ''), (59, '26', 'Heat_Rejection', '11.67929132', '$11679291.32', '1', '0.0022637181549502415', '2', 'ac26', 'million', '', ''), (60, '27', 'Special_Materials', '0.0', '$0.0', '1', '0.0', '2', 'ac27', 'million', '', ''), (61, '28', 'Digital_Twin/Simulator', '5.0', '$5000000.0', '1', '0.0009691162301405122', '2', 'ac28', 'million', '', ''), (62, '29', 'Contingency_on_Direct_Capital_Costs', '0.0', '$0.0', '1', '0.0', '2', 'ac29', 'million', '', ''), (63, '30', 'Capitalized_Indirect_Service_Costs_(CISC)', '71.59197058', '$71591970.58', '0', '0.013876188127364011', '', 'ac30', 'million', '', ''), (64, '31', 'Field_Indirect_Costs', '14.31839412', '$14318394.120000001', '1', '0.0027752376262480953', '3', 'ac31', 'million', '', ''), (65, '32', 'Construction_Supervision', '35.79598529', '$35795985.29', '1', '0.0069380940636820055', '3', 'ac32', 'million', '', ''), (66, '33', 'Commissioning_and_Start-Up_Costs', '0.0', '$0.0', '1', '0.0', '3', 'ac33', 'million', '', ''), (67, '34', 'Demonstration_Test_Run', '0.0', '$0.0', '1', '0.0', '3', 'ac34', 'million', '', ''), (68, '35', 'Design_Services_Offsite', '21.47759117', '$21477591.17', '1', '0.004162856437433911', '3', 'ac35', 'million', '', ''), (69, '36', 'PM/CM_Services_Offsite', '0.0', '$0.0', '1', '0.0', '3', 'ac36', 'million', '', ''), (70, '37', 'Design_Servies_Offsite', '0.0', '$0.0', '1', '0.0', '3', 'ac37', 'million', '', ''), (71, '38', 'PM/CM_Services_Onsite', '0.0', '$0.0', '1', '0.0', '3', 'ac38', 'million', '', ''), (72, '39', 'Contingency_on_Support_Services', '0.0', '$0.0', '1', '0.0', '3', 'ac39', 'million', '', ''), (73, '40', "Capitalized_Owner's_Cost_(COC)", '155.7811156', '$155781115.6', '0', '0.030194001495471065', '', 'ac40', 'million', '', ''), (74, '50', 'Capitalized_Supplementary_Costs_(CSC)', '37.83719261', '$37837192.61', '0', '0.00733372749226073', '', 'ac50', 'million', '', ''), (75, '51', 'Shipping_and_Transportation_Costs', '8.0', '$8000000.0', '1', '0.0015505859682248195', '5', 'ac51', 'million', '', ''), (76, '52', 'Spare_Parts', '7.323124886', '$7323124.886', '1', '0.0014193918364736975', '5', 'ac52', 'million', '', ''), (77, '53', 'Taxes', '0.0', '$0.0', '1', '0.0', '5', 'ac53', 'million', '', ''), (78, '54', 'Insurance', '1.0', '$1000000.0', '1', '0.00019382324602810244', '5', 'ac54', 'million', '', ''), (79, '55', 'Initial_Fuel_Load', '21.51406772', '$21514067.72', '1', '0.004169926440758817', '5', 'ac55', 'million', '', ''), (80, '58', 'Decommissioning_Costs', '0.0', '$0.0', '1', '0.0', '5', 'ac58', 'million', '', ''), (81, '59', 'Contingency_on_Supplementary_Costs', '0.0', '$0.0', '1', '0.0', '5', 'ac59', 'million', '', ''), (82, '60', 'Capitalized_Financial_Costs_(CFC)', '195.4094412', '$195409441.20000002', '0', '0.03787489219792162', '', 'ac60', 'million', '', ''), (83, '61', 'Escalation', '20.125', '$20125000.0', '1', '0.003900692826315562', '6', 'ac61', 'million', '', ''), (84, '62', 'Fees', '0.0', '$0.0', '1', '0.0', '6', 'ac62', 'million', '', ''), (85, '63', 'Interest_During_Construction_(IDC)', '175.2844412', '$175284441.20000002', '1', '0.033974199371606055', '6', 'ac63', 'million', '', ''), (86, '69', 'Contingency_on_Capitalized_Financial_Costs', '0.0', '$0.0', '1', '0.0', '6', 'ac69', 'million', '', ''), (87, 'OCC', 'Overnight_Capital_Cost_(OCC)', '1587.572359', '$1587572359.0', '0', '0.307708427925872', 'OC', 'acOCC', 'million', '', ''), (88, 'TCC', 'Total_Capital_Cost_(TCC)', '1782.981801', '$1782981801.0', '0', '0.3455833202788522', 'TC', 'acTCC', 'million', '', ''), (89, 'O&M', 'Operations_and_Maintenance', '5.69490028', '$5694900.279999999', '0', '0.0011038040580759493', 'O&', 'acO&M', 'million', '', ''), (90, 'Fuel', 'Fuel', '0.1090042081', '$109004.2081', '0', '2.1127549444664777e-05', 'Fue', 'acFuel', 'million', '', ''), (91, '81', 'Deuterium', '0.04739117657', '$47391.176569999996', '1', '9.185511675888353e-06', '8', 'ac81', 'million', '', '');
/*!40000 ALTER TABLE `mirror_acco` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mirror_alg`
--

DROP TABLE IF EXISTS `mirror_alg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mirror_alg` (
  `ind` int DEFAULT NULL,
  `alg_name` varchar(20) NOT NULL,
  `alg_for` text,
  `alg_description` text,
  `alg_python` text,
  `alg_formulation` text,
  `alg_units` text,
  PRIMARY KEY (`alg_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mirror_alg`
--

LOCK TABLES `mirror_alg` WRITE;
/*!40000 ALTER TABLE `mirror_alg` DISABLE KEYS */;
INSERT INTO `mirror_alg` VALUES ('1', '__init__', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('2', 'add_account', 'v', 'Add an account to the cost_account object.', 'MirrorFunc', 'TODO', 'TODO'), ('3', 'generate_report', 'v', 'Generate a report based on user input.', 'MirrorFunc', 'TODO', 'TODO'), ('4', 'learning_credit', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('5', 'Account_C20', 'c', 'Account C20 Rollup', 'MirrorFunc', 'TODO', 'million'), ('6', 'Account_C21', 'c', 'Account C21 Rollup', 'MirrorFunc', 'TODO', 'million'), ('7', 'Account_C21_1', 'c', 'Account C211 Rollup', 'MirrorFunc', 'TODO', 'million'), ('8', 'Account_C21_2', 'c', 'Account C212 Rollup', 'MirrorFunc', 'TODO', 'million'), ('9', 'Account_C21_3', 'c', 'Account C213 Rollup', 'MirrorFunc', 'TODO', 'million'), ('10', 'Account_C21_4', 'c', 'Account C214 Rollup', 'MirrorFunc', 'TODO', 'million'), ('11', 'Account_C21_5', 'c', 'Account C215 Rollup', 'MirrorFunc', 'TODO', 'million'), ('12', 'Account_C21_6', 'c', 'Account C216 Rollup', 'MirrorFunc', 'TODO', 'million'), ('13', 'Account_C21_7', 'c', 'Account C217 Rollup', 'MirrorFunc', 'TODO', 'million'), ('14', 'Account_C21_8', 'c', 'Account C218 Rollup', 'MirrorFunc', 'TODO', 'million'), ('15', 'Account_C21_9', 'c', 'Account C219 Rollup', 'MirrorFunc', 'TODO', 'million'), ('16', 'Account_C21_10', 'c', 'Account C2110 Rollup', 'MirrorFunc', 'TODO', 'million'), ('17', 'Account_C21_11', 'c', 'Account C2111 Rollup', 'MirrorFunc', 'TODO', 'million'), ('18', 'Account_C21_12', 'c', 'Account C2112 Rollup', 'MirrorFunc', 'TODO', 'million'), ('19', 'Account_C21_13', 'c', 'Account C2113 Rollup', 'MirrorFunc', 'TODO', 'million'), ('20', 'Account_C21_14', 'c', 'Account C2114 Rollup', 'MirrorFunc', 'TODO', 'million'), ('21', 'Account_C21_15', 'c', 'Account C2115 Rollup', 'MirrorFunc', 'TODO', 'million'), ('22', 'Account_C21_16', 'c', 'Account C2116 Rollup', 'MirrorFunc', 'TODO', 'million'), ('23', 'Account_C21_17', 'c', 'Account C2117 Rollup', 'MirrorFunc', 'TODO', 'million'), ('24', 'Account_C22', 'c', 'Account C22 Rollup', 'MirrorFunc', 'TODO', 'million'), ('25', 'Account_C22_1', 'c', 'Account C221 Rollup', 'MirrorFunc', 'TODO', 'million'), ('26', 'Account_C22_1_1', 'c', 'Account C2211 Rollup', 'MirrorFunc', 'TODO', 'million'), ('27', 'Account_C22_1_2', 'c', 'Account C2212 Rollup', 'MirrorFunc', 'TODO', 'million'), ('28', 'Account_C22_1_3', 'c', 'Account C2213 Rollup', 'MirrorFunc', 'TODO', 'million'), ('29', 'Account_C22_1_3_1', 'c', 'Account C22131 Rollup', 'MirrorFunc', 'TODO', 'million'), ('30', 'Account_C22_1_3_2', 'c', 'Account C22132 Rollup', 'MirrorFunc', 'TODO', 'million'), ('31', 'Account_C22_1_3_3', 'c', 'Account C22133 Rollup', 'MirrorFunc', 'TODO', 'million'), ('32', 'Account_C22_1_4', 'c', 'Account C2214 Rollup', 'MirrorFunc', 'TODO', 'million'), ('33', 'Account_C22_1_4_1', 'c', 'Account C22141 Rollup', 'MirrorFunc', 'TODO', 'million'), ('34', 'Account_C22_1_4_2', 'c', 'Account C22142 Rollup', 'MirrorFunc', 'TODO', 'million'), ('35', 'Account_C22_1_4_3', 'c', 'Account C22143 Rollup', 'MirrorFunc', 'TODO', 'million'), ('36', 'Account_C22_1_5', 'c', 'Account C2215 Rollup', 'MirrorFunc', 'TODO', 'million'), ('37', 'Account_C22_1_6', 'c', 'Account C2216 Rollup', 'MirrorFunc', 'TODO', 'million'), ('38', 'Account_C22_1_6_2', 'c', 'Account C22162 Rollup', 'MirrorFunc', 'TODO', 'million'), ('39', 'Account_C22_1_6_3', 'c', 'Account C22163 Rollup', 'MirrorFunc', 'TODO', 'million'), ('40', 'Account_C22_1_6_4', 'c', 'Account C22164 Rollup', 'MirrorFunc', 'TODO', 'million'), ('41', 'Account_C22_1_7', 'c', 'Account C2217 Rollup', 'MirrorFunc', 'TODO', 'million'), ('42', 'Account_C22_1_8', 'c', 'Account C2218 Rollup', 'MirrorFunc', 'TODO', 'million'), ('43', 'Account_C22_1_9', 'c', 'Account C2219 Rollup', 'MirrorFunc', 'TODO', 'million'), ('44', 'Account_C22_1_11', 'c', 'Account C22111 Rollup', 'MirrorFunc', 'TODO', 'million'), ('45', 'Account_C22_2', 'c', 'Account C222 Rollup', 'MirrorFunc', 'TODO', 'million'), ('46', 'Account_C22_2_1', 'c', 'Account C2221 Rollup', 'MirrorFunc', 'TODO', 'million'), ('47', 'Account_C22_2_2', 'c', 'Account C2222 Rollup', 'MirrorFunc', 'TODO', 'million'), ('48', 'Account_C22_2_3', 'c', 'Account C2223 Rollup', 'MirrorFunc', 'TODO', 'million'), ('49', 'Account_C22_3', 'c', 'Account C223 Rollup', 'MirrorFunc', 'TODO', 'million'), ('50', 'Account_C22_4', 'c', 'Account C224 Rollup', 'MirrorFunc', 'TODO', 'million'), ('51', 'Account_C22_5', 'c', 'Account C225 Rollup', 'MirrorFunc', 'TODO', 'million'), ('52', 'Account_C22_6', 'c', 'Account C226 Rollup', 'MirrorFunc', 'TODO', 'million'), ('53', 'Account_C22_7', 'c', 'Account C227 Rollup', 'MirrorFunc', 'TODO', 'million'), ('54', 'Account_C23', 'c', 'Account C23 Rollup', 'MirrorFunc', 'TODO', 'million'), ('55', 'Account_C24', 'c', 'Account C24 Rollup', 'MirrorFunc', 'TODO', 'million'), ('56', 'Account_C25', 'c', 'Account C25 Rollup', 'MirrorFunc', 'TODO', 'million'), ('57', 'Account_C26', 'c', 'Account C26 Rollup', 'MirrorFunc', 'TODO', 'million'), ('58', 'Account_C27', 'c', 'Account C27 Rollup', 'MirrorFunc', 'TODO', 'million'), ('59', 'Account_C28', 'c', 'Account C28 Rollup', 'MirrorFunc', 'TODO', 'million'), ('60', 'Account_C29', 'c', 'Account C29 Rollup', 'MirrorFunc', 'TODO', 'million'), ('61', 'Account_OCC', 'c', 'Account OCC Rollup', 'MirrorFunc', 'TODO', 'million'), ('62', 'Account_TCC', 'c', 'Account TCC Rollup', 'MirrorFunc', 'TODO', 'million'), ('63', 'Account_C90', 'c', 'Account C90 Rollup', 'MirrorFunc', 'TODO', 'million'), ('64', 'PbLi_density', 'v', 'Returns PbLi density (kg/m^3). Assumes the PbLi is a eutectic, which has', 'MirrorFunc', 'TODO', 'TODO'), ('65', 'Li_price', 'v', 'Return Li price (USD/kg) for enrichment levels above 90% 6Li', 'MirrorFunc', 'TODO', 'TODO'), ('66', 'PbLi_price', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('67', 'V_cylindrical_shell', 'v', 'Return volume of a cylindrical shell', 'MirrorFunc', 'TODO', 'TODO'), ('68', 'V_inverse_triangular_washer', 'v', 'Return volume of cylindrical inverse triangular washer.', 'MirrorFunc', 'TODO', 'TODO'), ('69', 'generate_inputs', 'v', 'Return a dict containing all inputs for a techno-economic analysis.', 'MirrorFunc', 'TODO', 'TODO'), ('70', 'create_radial_build', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('71', 'add_new_layer', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('72', 'add_fractional_layer', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('73', 'build_central_cell', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('74', 'central_cell_cost', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('75', 'central_cell', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('76', 'expander_cell_cost', 'v', 'Each expander cell is made up of:', 'MirrorFunc', 'TODO', 'TODO'), ('77', 'HF_magnet_cost', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('78', 'LF_magnet_cost', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('79', 'CF_magnet_cost', 'v', 'None', 'MirrorFunc', 'TODO', 'TODO'), ('80', 'HF_magnet_shield_cost', 'v', 'The HF coils have annular shield with a U-shaped cross section:', 'MirrorFunc', 'TODO', 'TODO');
/*!40000 ALTER TABLE `mirror_alg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mirror_var`
--

DROP TABLE IF EXISTS `mirror_var`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mirror_var` (
  `ind` int DEFAULT NULL,
  `var_name` varchar(30) NOT NULL,
  `var_description` text,
  `var_value` double DEFAULT NULL,
  `var_unit` text,
  `var_alg` text,
  `var_need` text,
  `v_linked` text,
  `user_input` int DEFAULT NULL,
  PRIMARY KEY (`var_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mirror_var`
--

LOCK TABLES `mirror_var` WRITE;
/*!40000 ALTER TABLE `mirror_var` DISABLE KEYS */;
INSERT INTO `mirror_var` VALUES ('1', 'E_DT', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('2', 'E_alpha', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('3', 'E_n', 'str', '', 'TODO', 'E_DT, E_alpha', 'TODO', 'TODO', ''), ('4', 'm_T', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('5', 'm_D', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('6', 'm_6Li', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('7', 'Wh_to_BTU', 'float', '3.41214', 'TODO', '', 'TODO', 'TODO', ''), ('8', 'indentation', 'int', '0', 'TODO', '', 'TODO', 'TODO', ''), ('9', 'indented_name', 'str', '', 'TODO', 'account_name, account_number, indentation', 'TODO', 'TODO', ''), ('10', 'inputs', 'str', '', 'TODO', 'NOAK, P_ECH, P_ICRH, P_NBI, P_f, P_f_L, application, availability, blanket_coolant_fraction, blanket_coolant_material, blanket_structural_fraction, blanket_structural_material, blanket_thickness, construction_time, cost_file, discount, first_wall_material, first_wall_thickness, generate_inputs, include_contingency, include_decommissioning, include_licensing, include_tax, kwargs, lifetime, method, multiplier_material, multiplier_thickness, n_unit, outer_vessel_thickness, replacement, save, vacuum_gap_CC, vacuum_vessel_material, vacuum_vessel_thickness', 'TODO', 'TODO', ''), ('11', 'cost_data', 'str', '', 'TODO', 'cost_account', 'TODO', 'TODO', ''), ('12', 'L_magnet_to_magnet', 'str', '', 'TODO', 'inputs', 'TODO', 'TODO', ''), ('13', 'L_cylinder', 'str', '', 'TODO', 'L_magnet_to_magnet', 'TODO', 'TODO', ''), ('14', 'expander_cell_cost_result', 'str', '', 'TODO', 'expander_cell_cost, inputs', 'TODO', 'TODO', ''), ('15', 'end_plug_cylindrical_part', 'str', '', 'TODO', 'L_cylinder, central_cell, inputs', 'TODO', 'TODO', ''), ('16', 'end_plug_cylindrical_part_cost', 'str', '', 'TODO', 'end_plug_cylindrical_part', 'TODO', 'TODO', ''), ('17', 'central_cell_cylindrical_part', 'str', '', 'TODO', 'central_cell, inputs', 'TODO', 'TODO', ''), ('18', 'central_cell_cylindrical_part_cost', 'str', '', 'TODO', 'central_cell_cylindrical_part', 'TODO', 'TODO', ''), ('19', 'total_cost', 'str', '', 'TODO', 'central_cell_cylindrical_part_cost, end_plug_cylindrical_part_cost, expander_cell_cost_result', 'TODO', 'TODO', ''), ('20', 'cost_factor', 'str', '', 'TODO', 'inputs, np', 'TODO', 'TODO', ''), ('21', 'cost_pump', 'int', '40000', 'TODO', '', 'TODO', 'TODO', ''), ('22', 'vpump_cap', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('23', 'no_vpumps', 'str', '', 'TODO', 'inputs, vpump_cap', 'TODO', 'TODO', ''), ('24', 'axis_t', 'str', '', 'TODO', 'inputs, np', 'TODO', 'TODO', ''), ('25', 'axis_ir', 'str', '', 'TODO', 'axis_t', 'TODO', 'TODO', ''), ('26', 'lr', 'str', '', 'TODO', '', 'TODO', 'TODO', ''), ('27', 'constructionworker', 'str', '', 'TODO', 'axis_ir', 'TODO', 'TODO', ''), ('28', 'C_22_1_11_in', 'str', '', 'TODO', 'inputs, lr', 'TODO', 'TODO', ''), ('29', 'C_22_1_11_1_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('30', 'C_22_1_11_2_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('31', 'C_22_1_11_3_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('32', 'C_22_1_11_4_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('33', 'C_22_1_11_5_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('34', 'C_22_1_11_6_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('35', 'C_22_1_11_7_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('36', 'C_22_1_11_8_in', 'int', '0', 'TODO', '', 'TODO', 'TODO', ''), ('37', 'C_22_1_11_9_in', 'str', '', 'TODO', 'constructionworker, inputs, lr', 'TODO', 'TODO', ''), ('38', 'C_22_1_11_10_in', 'int', '0', 'TODO', '', 'TODO', 'TODO', ''), ('39', 'C220111', 'str', '', 'TODO', 'C_22_1_11_10_in, C_22_1_11_1_in, C_22_1_11_2_in, C_22_1_11_3_in, C_22_1_11_4_in, C_22_1_11_5_in, C_22_1_11_6_in, C_22_1_11_7_in, C_22_1_11_8_in, C_22_1_11_9_in, C_22_1_11_in', 'TODO', 'TODO', ''), ('40', 'inflation', 'float', '1.43', 'TODO', '', 'TODO', 'TODO', ''), ('41', 'C2205010ITER', 'str', '', 'TODO', 'inflation', 'TODO', 'TODO', ''), ('42', 'C2205020ITER', 'str', '', 'TODO', 'inflation', 'TODO', 'TODO', ''), ('43', 'C2205030ITER', 'str', '', 'TODO', 'inflation', 'TODO', 'TODO', ''), ('44', 'C2205040ITER', 'str', '', 'TODO', 'inflation', 'TODO', 'TODO', ''), ('45', 'C2205050ITER', 'str', '', 'TODO', 'inflation', 'TODO', 'TODO', ''), ('46', 'C2205060ITER', 'str', '', 'TODO', 'inflation', 'TODO', 'TODO', ''), ('47', 'lcredit', 'float', '0.8', 'TODO', '', 'TODO', 'TODO', ''), ('48', 'ltoak', 'str', '', 'TODO', 'lcredit, np', 'TODO', 'TODO', ''), ('49', 'C220501', 'str', '', 'TODO', 'C2205010ITER, ltoak', 'TODO', 'TODO', ''), ('50', 'C220502', 'str', '', 'TODO', 'C2205020ITER, ltoak', 'TODO', 'TODO', ''), ('51', 'C220503', 'str', '', 'TODO', 'C2205030ITER, ltoak', 'TODO', 'TODO', ''), ('52', 'C220504', 'str', '', 'TODO', 'C2205040ITER, ltoak', 'TODO', 'TODO', ''), ('53', 'C220505', 'str', '', 'TODO', 'C2205050ITER, ltoak', 'TODO', 'TODO', ''), ('54', 'C220506', 'str', '', 'TODO', 'C2205060ITER, ltoak', 'TODO', 'TODO', ''), ('55', 'C220500', 'str', '', 'TODO', 'C220501, C220502, C220503, C220504, C220505, C220506', 'TODO', 'TODO', ''), ('56', 'f_cr', 'float', '0.09', 'TODO', '', 'TODO', 'TODO', ''), ('57', 'f_6Li_natural', 'float', '0.075', 'TODO', '', 'TODO', 'TODO', ''), ('58', 'rho_6Li', 'float', '460.0', 'TODO', '', 'TODO', 'TODO', ''), ('59', 'rho_7Li', 'float', '537.0', 'TODO', '', 'TODO', 'TODO', ''), ('60', 'T_K', 'str', '', 'TODO', 'T', 'TODO', 'TODO', ''), ('61', 'rho_PbLi', 'str', '', 'TODO', 'T_K', 'TODO', 'TODO', ''), ('62', 'P_6Li075', 'float', '15.152', 'TODO', '', 'TODO', 'TODO', ''), ('63', 'P_6Li90', 'int', '70', 'TODO', '', 'TODO', 'TODO', ''), ('64', 'f', 'list', '(0.9, 0.99, 0.999, 0.9999, 0.99999)', 'TODO', '', 'TODO', 'TODO', ''), ('65', 'Cf', 'list', '(1, 2, 4, 8, 16)', 'TODO', '', 'TODO', 'TODO', ''), ('66', 'f_interp', 'str', '', 'TODO', 'Cf, f, scipy', 'TODO', 'TODO', ''), ('67', 'f_Li', 'float', '0.17', 'TODO', '', 'TODO', 'TODO', ''), ('68', 'f_Pb', 'str', '', 'TODO', 'f_Li', 'TODO', 'TODO', ''), ('69', 'P_Li', 'str', '', 'TODO', 'Li_price, f_6Li', 'TODO', 'TODO', ''), ('70', 'P_PbLi', 'str', '', 'TODO', 'P_Li, P_Pb, f_Li, f_Pb', 'TODO', 'TODO', ''), ('71', 'P_f_CC', 'str', '', 'TODO', 'P_f, P_f_EP', 'TODO', 'TODO', ''), ('72', 'L_CC', 'str', '', 'TODO', 'P_f_CC, P_f_L', 'TODO', 'TODO', ''), ('73', 'L_CF', 'float', '1.0', 'TODO', '', 'TODO', 'TODO', ''), ('74', 'L', 'str', '', 'TODO', 'L_CC, L_EC, L_EP', 'TODO', 'TODO', ''), ('75', 'V_vac', 'str', '', 'TODO', 'L, a_EC, np', 'TODO', 'TODO', ''), ('76', 'P_alpha', 'str', '', 'TODO', 'E_DT, E_alpha, P_f', 'TODO', 'TODO', ''), ('77', 'P_n', 'str', '', 'TODO', 'P_alpha, P_f', 'TODO', 'TODO', ''), ('78', 'P_ine', 'str', '', 'TODO', 'P_ECH, P_ICRH, P_NBI, eta_ECH, eta_ICRH, eta_NBI', 'TODO', 'TODO', ''), ('79', 'P_pump', 'str', '', 'TODO', 'M_n, P_n, f_pump', 'TODO', 'TODO', ''), ('80', 'P_sub_cont', 'str', '', 'TODO', 'P_f, f_sub', 'TODO', 'TODO', ''), ('81', 'P_cryo', 'str', '', 'TODO', 'P_f, f_cryo', 'TODO', 'TODO', ''), ('82', 'P_other', 'str', '', 'TODO', 'P_cryo, P_pump, P_sub_cont', 'TODO', 'TODO', ''), ('83', 'P_in', 'str', '', 'TODO', 'P_ECH, P_ICRH, P_NBI', 'TODO', 'TODO', ''), ('84', 'P_th', 'str', '', 'TODO', 'M_n, P_n, P_pump, eta_pump', 'TODO', 'TODO', ''), ('85', 'P_the', 'str', '', 'TODO', 'P_th, eta_th', 'TODO', 'TODO', ''), ('86', 'P_DEC', 'str', '', 'TODO', 'P_alpha, P_in', 'TODO', 'TODO', ''), ('87', 'P_DECe', 'str', '', 'TODO', 'P_DEC, eta_DEC', 'TODO', 'TODO', ''), ('88', 'P_egross', 'str', '', 'TODO', 'P_DECe, P_the', 'TODO', 'TODO', ''), ('89', 'P_enet', 'str', '', 'TODO', 'P_egross, P_ine, P_other', 'TODO', 'TODO', ''), ('90', 'f_aux', 'str', '', 'TODO', 'P_aux, P_egross', 'TODO', 'TODO', ''), ('91', 'Q_sci', 'str', '', 'TODO', 'P_f, P_in', 'TODO', 'TODO', ''), ('92', 'Q_eng', 'str', '', 'TODO', 'P_egross, P_ine, P_other', 'TODO', 'TODO', ''), ('93', 'f_refrac', 'str', '', 'TODO', 'Q_eng', 'TODO', 'TODO', ''), ('94', 'run_name', 'str', '', 'TODO', 'P_f, float', 'TODO', 'TODO', ''), ('95', 'cost_file_full', 'str', '', 'TODO', 'cost_file, pkg_resources', 'TODO', 'TODO', ''), ('96', 'new_data', 'str', '', 'TODO', 'f_vol, material, name, pd, thickness', 'TODO', 'TODO', ''), ('97', 'r_in', 'str', '', 'TODO', 'data', 'TODO', 'TODO', ''), ('98', 'r_out', 'str', '', 'TODO', 'data', 'TODO', 'TODO', ''), ('99', 'radial_build', 'str', '', 'TODO', 'create_radial_build, inputs', 'TODO', 'TODO', ''), ('100', 'filename', 'str', '', 'TODO', 'inputs', 'TODO', 'TODO', ''), ('101', 'T', 'int', '300', 'TODO', '', 'TODO', 'TODO', ''), ('102', 'material', 'str', '', 'TODO', 'i, radial_build', 'TODO', 'TODO', ''), ('103', 'f_6Li', 'float', '0.075', 'TODO', '', 'TODO', 'TODO', ''), ('104', 'radius', 'str', '', 'TODO', 'inputs', 'TODO', 'TODO', ''), ('105', 'thickness', 'str', '', 'TODO', 'inputs', 'TODO', 'TODO', ''), ('106', 'vv_material', 'str', '', 'TODO', 'inputs', 'TODO', 'TODO', ''), ('107', 'V_end_cap', 'str', '', 'TODO', 'np, radius, thickness', 'TODO', 'TODO', ''), ('108', 'M_end_cap', 'str', '', 'TODO', 'V_end_cap, cost_data, vv_material', 'TODO', 'TODO', ''), ('109', 'C_end_cap', 'str', '', 'TODO', 'M_end_cap, cost_data, vv_material', 'TODO', 'TODO', ''), ('110', 'total', 'str', '', 'TODO', 'C_end_cap, radial_build', 'TODO', 'TODO', ''), ('111', 'cost', 'float', '29.1', 'TODO', '', 'TODO', 'TODO', ''), ('112', 'a_M', 'float', '0.15', 'TODO', '', 'TODO', 'TODO', ''), ('113', 'a_CC', 'float', '0.54', 'TODO', '', 'TODO', 'TODO', ''), ('114', 'a_0', 'float', '0.7', 'TODO', '', 'TODO', 'TODO', ''), ('115', 'length', 'float', '0.5', 'TODO', '', 'TODO', 'TODO', ''), ('116', 'r_gap', 'float', '0.1', 'TODO', '', 'TODO', 'TODO', ''), ('117', 'r_vv', 'float', '0.01', 'TODO', '', 'TODO', 'TODO', ''), ('118', 'r_magnet', 'float', '1.5', 'TODO', '', 'TODO', 'TODO', ''), ('119', 'r_cryostat', 'float', '1.0', 'TODO', '', 'TODO', 'TODO', ''), ('120', 'f_vol', 'float', '0.9', 'TODO', '', 'TODO', 'TODO', ''), ('121', 'V_radially_inner_cylinder', 'str', '', 'TODO', 'V_cylindrical_shell, f_vol, length, r_in, r_out', 'TODO', 'TODO', ''), ('122', 'length_cc_cylinder', 'float', '0.5', 'TODO', '', 'TODO', 'TODO', ''), ('123', 'r_in_cc', 'str', '', 'TODO', 'a_CC, r_gap, r_vv', 'TODO', 'TODO', ''), ('124', 'r_out_cc', 'str', '', 'TODO', 'r_in_cc', 'TODO', 'TODO', ''), ('125', 'V_cc_cylinder', 'str', '', 'TODO', 'V_cylindrical_shell, f_vol, length_cc_cylinder, r_in_cc, r_out_cc', 'TODO', 'TODO', ''), ('126', 'V_cc_triangle', 'str', '', 'TODO', 'V_inverse_triangular_washer, f_vol, length_cc_cylinder, r_in, r_in_cc', 'TODO', 'TODO', ''), ('127', 'length_ep_cylinder', 'float', '0.5', 'TODO', '', 'TODO', 'TODO', ''), ('128', 'r_in_ep', 'str', '', 'TODO', 'a_0, r_gap, r_vv', 'TODO', 'TODO', ''), ('129', 'r_out_ep', 'str', '', 'TODO', 'r_in_ep', 'TODO', 'TODO', ''), ('130', 'V_ep_cylinder', 'str', '', 'TODO', 'V_cylindrical_shell, f_vol, length_ep_cylinder, r_in_ep, r_out_ep', 'TODO', 'TODO', ''), ('131', 'V_ep_triangle', 'str', '', 'TODO', 'V_inverse_triangular_washer, f_vol, length_ep_cylinder, r_in, r_in_ep', 'TODO', 'TODO', ''), ('132', 'V_total_cc_facing', 'str', '', 'TODO', 'V_cc_cylinder, V_cc_triangle, V_ep_cylinder, V_ep_triangle, V_radially_inner_cylinder', 'TODO', 'TODO', ''), ('133', 'V_total_ec_facing', 'str', '', 'TODO', 'V_ep_cylinder, V_ep_triangle, V_radially_inner_cylinder', 'TODO', 'TODO', ''), ('134', 'V_total', 'str', '', 'TODO', 'V_total_cc_facing, V_total_ec_facing', 'TODO', 'TODO', ''), ('135', 'mass', 'str', '', 'TODO', 'V_total, cost_data, material', 'TODO', 'TODO', '');
/*!40000 ALTER TABLE `mirror_var` ENABLE KEYS */;
UNLOCK TABLES;

/* TODO add mirror vars and others */

--
-- Dumping events for database 'accert_db'
--

--
-- Dumping routines for database 'accert_db'
--
/*!50003 DROP PROCEDURE IF EXISTS `cal_direct_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `cal_direct_cost_elements`(IN acc_table VARCHAR(50),
																		IN cel_table varchar(50))
BEGIN
    DECLARE tprn DECIMAL(18,6);

    -- Calculate tprn (sum of 'prn' in the account table)
    SET @query = CONCAT('SELECT SUM(t1.prn) INTO @tprn
                         FROM ', acc_table, ' AS t1
                         LEFT JOIN ', acc_table, ' AS t2
                         ON t1.code_of_account = t2.supaccount
                         WHERE t2.code_of_account IS NULL
                         AND t1.code_of_account != ''2''
                         AND t1.code_of_account != ''2C'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    -- Get the calculated tprn value
    SET tprn = @tprn;

    -- Select the calculated 'fac', 'lab', and 'mat' values
    SET @query = CONCAT('SELECT cost_2017 / ', tprn, ' AS fac FROM ', cel_table, '
                        WHERE account = ''2'' AND cost_element = ''2c_fac'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET @query = CONCAT('SELECT cost_2017 / ', tprn, ' AS lab FROM ', cel_table, '
                        WHERE account = ''2'' AND cost_element = ''2c_lab'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET @query = CONCAT('SELECT cost_2017 / ', tprn, ' AS mat FROM ', cel_table, '
                        WHERE account = ''2'' AND cost_element = ''2c_mat'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET @query = CONCAT('SELECT 
        (SELECT cost_2017 / ', tprn, ' FROM ', cel_table, ' WHERE account = ''2'' AND cost_element = ''2c_fac'') AS fac,
        (SELECT cost_2017 / ', tprn, ' FROM ', cel_table, ' WHERE account = ''2'' AND cost_element = ''2c_lab'') AS lab,
        (SELECT cost_2017 / ', tprn, ' FROM ', cel_table, ' WHERE account = ''2'' AND cost_element = ''2c_mat'') AS mat;');
    
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_affected_accounts` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_affected_accounts`(IN acc_table VARCHAR(50),
																		IN var_table VARCHAR(50))
BEGIN
	SET @stmt = CONCAT("SELECT va.var_name, (SELECT GROUP_CONCAT(ac.code_of_account SEPARATOR ', ')
        FROM ", acc_table, " ac
        WHERE FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0) AS ac_affected
                        FROM
                        (SELECT * FROM ",var_table,"
                        WHERE user_input = 1) as va
                        WHERE (SELECT GROUP_CONCAT(ac.code_of_account SEPARATOR ', ')
								FROM ", acc_table, " ac
						WHERE FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0) IS NOT NULL
                        ");
	PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_affected_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_affected_cost_elements`(IN cel_table varchar(50),
                                                                              IN var_table varchar(50))
BEGIN
    SET @stmt = CONCAT("SELECT va.var_name, (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
                        FROM
                        (SELECT * FROM ",var_table,"
                        WHERE user_input = 1) as va
                        WHERE (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
								FROM ", cel_table, " ce
						WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) IS NOT NULL
                        ");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_affected_cost_elements_w_dis` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_affected_cost_elements_w_dis`(IN cel_table varchar(50),
                                                                              IN var_table varchar(50))
BEGIN
    SET @stmt = CONCAT("SELECT va.var_name,va.var_description, (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
                        FROM
                        (SELECT * FROM ",var_table,"
                        WHERE user_input = 1) as va
                        WHERE (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
								FROM cost_element ce
						WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) IS NOT NULL
                        ");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_changed_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_changed_cost_elements`(IN cel_table VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT cost_element, cost_2017
                        FROM ',cel_table,'
                        WHERE updated != 0
                        ORDER BY account, cost_element;');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_super_val` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_super_val`(IN table_name VARCHAR(50),
                                          IN var_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT v_linked FROM ', table_name, ' WHERE var_name = ?');
 PREPARE stmt FROM @stmt;
 SET @var_name = var_name;
 EXECUTE stmt USING @var_name;
 DEALLOCATE PREPARE stmt;
 END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_total_cost_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_total_cost_on_name`(IN table_name VARCHAR(50),
                                          IN tc_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT code_of_account, account_description, total_cost
                        FROM ', table_name, ' WHERE code_of_account = ?');
PREPARE stmt FROM @stmt;
SET @tc_name = tc_name;
EXECUTE stmt USING @tc_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_user_changed_variables` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_user_changed_variables`(IN table_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var_name,var_description, var_value, var_unit
                        FROM ', table_name, ' WHERE user_input = 1 ORDER BY var_name;');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_variable_info_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_variable_info_on_name`(IN table_name VARCHAR(50),
                                          IN var_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var_value, var_unit FROM ', table_name, ' WHERE var_name = ?');
PREPARE stmt FROM @stmt;
SET @var_name = var_name;
EXECUTE stmt USING @var_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_current_COAs` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `get_current_COAs`(IN table_name VARCHAR(50), 
                                  IN inp_id VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT code_of_account, 
                       ind FROM ', table_name, ' WHERE supaccount = ?');
    PREPARE stmt FROM @stmt;
    SET @inp_id = inp_id;
    EXECUTE stmt USING @inp_id;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_var_value_by_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `get_var_value_by_name`(IN table_name VARCHAR(50),
                                                                    IN `var_name` VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var_value FROM ', table_name, ' WHERE var_name = ?');
    PREPARE stmt FROM @stmt;
    SET @var_name = var_name;
    EXECUTE stmt USING @var_name;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `insert_new_COA` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `insert_new_COA`(IN table_name VARCHAR(50),
											IN ind INT,
											IN supaccount VARCHAR(50),
											IN level INT,
											IN code_of_account VARCHAR(50),
											IN account_description VARCHAR(50),
											IN total_cost INT,
											IN review_status VARCHAR(50),
											IN prn VARCHAR(50))
BEGIN
	SET @stmt = CONCAT('INSERT INTO ', table_name,
						' (ind, supaccount, level, code_of_account, account_description, 
							total_cost, review_status, prn) 
							VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
PREPARE stmt FROM @stmt;
SET @ind = ind;
SET @supaccount = supaccount;
SET @level = level;
SET @code_of_account = code_of_account;
SET @account_description = account_description;
SET @total_cost = total_cost;
SET @review_status = review_status;
SET @prn = prn;


EXECUTE stmt USING @ind, @supaccount, @level, @code_of_account, @account_description,
@total_cost, @review_status, @prn;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `insert_new_COA_gncoa` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `insert_new_COA_gncoa`(IN table_name VARCHAR(50),
											IN ind INT,
											IN supaccount VARCHAR(50),
											IN level INT,
											IN code_of_account VARCHAR(50),
											IN account_description VARCHAR(50),
											IN total_cost INT,
											IN review_status VARCHAR(50),
											IN prn VARCHAR(50),
                                            IN gncoa VARCHAR(50), 
                                            IN gn_level INT, 
                                            IN gn_supaccount VARCHAR(50), 
											IN gn_ind INT)
BEGIN
	SET @stmt = CONCAT('INSERT INTO ', table_name,
						' (ind, supaccount, level, code_of_account, account_description, 
							total_cost, review_status, prn, 
                            gncoa, gn_level, gn_supaccount, gn_ind) 
							VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)');
PREPARE stmt FROM @stmt;
SET @ind = ind;
SET @supaccount = supaccount;
SET @level = level;
SET @code_of_account = code_of_account;
SET @account_description = account_description;
SET @total_cost = total_cost;
SET @review_status = review_status;
SET @prn = prn;
SET @gncoa = gncoa; 
SET @gn_level = gn_level; 
SET @gn_supaccount = gn_supaccount;
SET @gn_ind = gn_ind;

EXECUTE stmt USING @ind, @supaccount, @level, @code_of_account, @account_description,
@total_cost, @review_status, @prn, @gncoa, @gn_level, @gn_supaccount, @gn_ind;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_account_all` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_account_all`(IN table_name varchar(50),
                                                                IN level int)
BEGIN
    SET @stmt=CONCAT('SELECT * FROM ',table_name,' WHERE level <= ?');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_account_simple` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_account_simple`(IN table_name varchar(50),
                                                                   IN level int)
BEGIN
    SET @stmt=CONCAT('SELECT ind,
                            code_of_account,
                            account_description,
                            total_cost,
                            level,
                            review_status
                            FROM ',table_name,' WHERE level <= ?');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_all` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_all`(IN acc_table varchar(50),
                                                                        IN  cel_table varchar(50),
                                                                        IN  level int)
BEGIN
    SET @stmt=CONCAT('SELECT acc.level,
                            rankedcoa.code_of_account as code_of_account,
                            acc.account_description,
                            sorted_ce.fac_cost,
                            sorted_ce.lab_cost,
                            sorted_ce.mat_cost,
                            acc.total_cost,
                            acc.review_status
                            FROM ',acc_table,' as acc
                            JOIN
                            (SELECT node.code_of_account AS COA , 
								CONCAT( REPEAT(" ", node.level), node.code_of_account) AS code_of_account
								FROM ',acc_table,' AS node
								ORDER BY node.ind) as rankedcoa
                                ON acc.code_of_account=rankedcoa.COA
                                JOIN (SELECT splt_act.code_of_account,
											   cef.cost_2017 AS fac_cost,
											   cel.cost_2017 AS lab_cost,
											   cem.cost_2017 AS mat_cost
										FROM 
											(SELECT code_of_account, 
													CONCAT(code_of_account, "_fac") AS fac_name,
													CONCAT(code_of_account, "_lab") AS lab_name,
													CONCAT(code_of_account, "_mat") AS mat_name
											 FROM ',acc_table,') AS splt_act
										LEFT JOIN ',cel_table,' AS cef
											ON cef.cost_element = splt_act.fac_name
										LEFT JOIN ',cel_table,' AS cel
											ON cel.cost_element = splt_act.lab_name
										LEFT JOIN ',cel_table,' AS cem
											ON cem.cost_element = splt_act.mat_name) as sorted_ce
                                    ON sorted_ce.code_of_account=acc.code_of_account
                                    WHERE acc.level <= ?
                                    ORDER BY acc.ind;');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_gn` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_gn`(
    IN acc_table VARCHAR(255),
    IN map_table VARCHAR(255),
    IN level INT
)
BEGIN
    SET @stmt = CONCAT(
        'SELECT rankedcoa.gncoa,
				map.gncoa_description,
                acc.total_cost,
                acc.gn_level,
                acc.review_status
         FROM ', acc_table, ' AS acc
         JOIN 
         (
             SELECT node.gncoa AS COA, 
                    CONCAT(REPEAT(" ", node.gn_level), node.gncoa) AS gncoa
             FROM ', acc_table, ' AS node
             ORDER BY node.gn_ind
         ) AS rankedcoa
         ON acc.gncoa = rankedcoa.COA
         JOIN ',map_table,' as map
         ON acc.gncoa = map.gncoa
         WHERE acc.gn_level <= ?
         ORDER BY acc.gn_ind;'
    );
    
    PREPARE stmt FROM @stmt;
    SET @level = level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_gn_all` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_gn_all`(IN acc_table varchar(50),
                                                                        IN  cel_table varchar(50),
                                                                        IN  level int)
BEGIN
    SET @stmt=CONCAT('SELECT acc.gn_level,
                            rankedcoa.gncoa as gncoa,
                            acc.account_description,
                            sorted_ce.fac_cost,
                            sorted_ce.lab_cost,
                            sorted_ce.mat_cost,
                            acc.total_cost,
                            acc.review_status
                            FROM ',acc_table,' as acc
                            JOIN
							 (SELECT node.gncoa AS COA, 
										CONCAT(REPEAT(" ", node.gn_level), node.gncoa) AS gncoa
								 FROM ', acc_table, ' AS node
								 ORDER BY node.gn_ind) AS rankedcoa
                                ON acc.gncoa=rankedcoa.COA
                                JOIN (SELECT splt_act.code_of_account,
											   cef.cost_2017 AS fac_cost,
											   cel.cost_2017 AS lab_cost,
											   cem.cost_2017 AS mat_cost
										FROM 
											(SELECT code_of_account, 
													CONCAT(code_of_account, "_fac") AS fac_name,
													CONCAT(code_of_account, "_lab") AS lab_name,
													CONCAT(code_of_account, "_mat") AS mat_name
											 FROM ',acc_table,') AS splt_act
										LEFT JOIN ',cel_table,' AS cef
											ON cef.cost_element = splt_act.fac_name
										LEFT JOIN ',cel_table,' AS cel
											ON cel.cost_element = splt_act.lab_name
										LEFT JOIN ',cel_table,' AS cem
											ON cem.cost_element = splt_act.mat_name) as sorted_ce
                                    ON sorted_ce.code_of_account=acc.code_of_account
                                    WHERE acc.gn_level <= ?
                                    ORDER BY acc.gn_ind;');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_simple` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_simple`(IN acc_table VARCHAR(255), IN level INT)
BEGIN
    SET @stmt = CONCAT('SELECT rankedcoa.code_of_account,
                    acc.account_description,
                    acc.total_cost,
                    acc.level,
                    acc.review_status
                    FROM ',acc_table,' as acc
                    JOIN
                    (SELECT node.code_of_account AS COA , 
                    CONCAT( REPEAT(" ", node.level), node.code_of_account) AS code_of_account
                    FROM ',acc_table,' AS node
                    ORDER BY node.ind) as rankedcoa
                    ON acc.code_of_account=rankedcoa.COA
                    WHERE acc.level <= ?
                    ORDER BY acc.ind;');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_table` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_table`(IN table_name VARCHAR(255))
BEGIN
    SET @stmt = CONCAT('SELECT * FROM ',table_name);
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_updated_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_updated_cost_elements`(IN cel_table VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT ind,
                                cost_element,
                                cost_2017,    
                                sup_cost_ele,
                                account,
                                updated
                        FROM ',cel_table,'
                        WHERE updated = 1');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_user_request_parameter` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_user_request_parameter`(IN all_col BOOLEAN,
                                                                           IN var_table VARCHAR(50), 
                                                                           IN cel_table VARCHAR(50))
BEGIN
    IF all_col THEN
		SET @stmt = CONCAT("SELECT va.ind, va.var_name, 
       (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
		FROM ",var_table," as va
		WHERE va.var_value IS NULL
		ORDER BY va.ind;");
    ELSE
        SET @stmt = CONCAT("SELECT va.var_name, 
       (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
		FROM ",var_table," as va
		WHERE va.var_value IS NULL
		ORDER BY va.ind;");
    END IF;
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_specific_row` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `remove_specific_row`(
    IN table_name VARCHAR(50),
    IN target_code VARCHAR(50)
)
BEGIN
    SET SQL_SAFE_UPDATES = 0;
    
    SET @stmt = CONCAT(
        'DELETE FROM ', table_name,
        ' WHERE code_of_account = \'', target_code, '\''
    );

    -- Debug: Print the constructed SQL statement
    SELECT @stmt;
    
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_account_table_by_gn_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_account_table_by_gn_level`(
    IN table_name VARCHAR(50),
    IN from_level INT,
    IN to_level INT
)
BEGIN
    SET SQL_SAFE_UPDATES = 0;

    SET @stmt = CONCAT(
        'UPDATE ', table_name, ',',
        '(SELECT a', to_level, '.gncoa AS ac', to_level, '_coa, ',
                'SUM(ua', from_level, '.total_cost) AS a', to_level, '_cal_total_cost ',
        'FROM ', table_name, ' AS ua', from_level,
        ' JOIN ', table_name, ' AS a', to_level,
        ' ON ua', from_level, '.gn_supaccount = a', to_level, '.gncoa ',
        'WHERE ua', from_level, '.gn_level = ', from_level,
        ' AND a', to_level, '.gn_level = ', to_level,
        ' GROUP BY a', to_level, '.gncoa) AS updated_ac', to_level,
        ' SET ',
        table_name, '.total_cost = updated_ac', to_level, '.a', to_level, '_cal_total_cost, ',
        table_name, '.review_status = \'Updated\' ',
        'WHERE ',
        table_name, '.gncoa = updated_ac', to_level, '.ac', to_level, '_coa'
    );

    -- Debug: Print the constructed SQL statement
    SELECT @stmt;

    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_account_table_by_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_account_table_by_level`(IN table_name varchar(50),
                                                                        IN from_level int, IN to_level int)
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name, ',',
                    '(SELECT a',to_level,'.code_of_account as ac',to_level,'_coa, ',
                            'sum(ua',from_level,'.total_cost) as a',to_level,'_cal_total_cost ',
                    'FROM ', table_name, ' as ua',from_level,
                    ' JOIN ', table_name, ' as a',to_level,
                    ' on ua',from_level,'.supaccount=a',to_level,'.code_of_account ',
                    'where ua',from_level,'.level=',from_level,
                    ' and a',to_level,'.level=',to_level,
                    ' group by a',to_level,'.code_of_account) as updated_ac',to_level,
                    ' SET ',
                    table_name,'.total_cost = updated_ac',to_level,'.a',to_level,'_cal_total_cost,',
                    table_name,'.review_status = \'Updated\' ',
                    'WHERE ',
                    table_name,'.code_of_account = updated_ac',to_level,'.ac',to_level,'_coa');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_cost_elements_by_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_cost_elements_by_level`(IN table_name varchar(50), 
                                                                  IN from_level int, IN to_level int)
BEGIN
    SET @stmt = CONCAT('UPDATE ', table_name, ',',
                        '(SELECT c',to_level,'.cost_element as ce',to_level,'_ce, ',
                            'sum(uc',from_level,'.cost_2017) as c',to_level,'_cal_total_cost ',
                        'FROM ', table_name, ' as uc',from_level,
                        ' JOIN ', table_name, ' as c',to_level,
                        ' on uc',from_level,'.sup_cost_ele=c',to_level,'.cost_element ',
                        'join account as ac',to_level,
                        ' on c',to_level,'.account = ac',to_level,'.code_of_account ',
                        'where ac',to_level,'.level=',to_level,
                        ' group by c',to_level,'.cost_element) as updated_ce',to_level,
                        ' SET ',
                        table_name,'.cost_2017 = updated_ce',to_level,'.c',to_level,'_cal_total_cost,',
                        table_name,'.updated = 1 ',
                        'WHERE ',
                        table_name,'.cost_element = updated_ce',to_level,'.ce',to_level,'_ce');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_lmt_account_2C` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_lmt_account_2C`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT sum(t1.total_cost) as tc, sum(t1.prn) as tprn FROM
                            ', acc_tabl_name, ' AS t1 LEFT JOIN ', acc_tabl_name, ' as t2
                            ON t1.code_of_account = t2.supaccount
                            WHERE t2.code_of_account IS NULL
                            and t1.code_of_account!=\'2\'
                            and t1.code_of_account!=\'2C\') as dircost
                        SET ', acc_tabl_name, '.total_cost = dircost.tc,
                        ', acc_tabl_name, '.prn=dircost.tprn,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2C\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_lmt_direct_cost` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_lmt_direct_cost`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT  (total_cost/prn) as talcost
                            FROM ', acc_tabl_name, ' as pre_acc
                            WHERE pre_acc.code_of_account =\'2C\') as calcost
                        SET ', acc_tabl_name, '.total_cost = calcost.talcost,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_cost_elements_2C_fac` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_cost_elements_2C_fac`(IN cel_tabl_name varchar(50),
                                                                    IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('SELECT sum(cef.cost_2017) from
                        (SELECT t1.code_of_account,
                        CONCAT(t1.code_of_account,\'_fac\') as fac_name
                        FROM ', acc_tabl_name, ' AS t1
                        LEFT JOIN ', acc_tabl_name, ' as t2
                        ON t1.code_of_account = t2.supaccount
                        WHERE t2.code_of_account IS NULL
                        and t1.code_of_account!=\'2\'
                        and t1.code_of_account!=\'2C\' )as ac
                        join ', cel_tabl_name, ' as cef
                                on cef.cost_element = ac.fac_name
                                where ac.code_of_account!=\'2C\'');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_cost_elements_2C_lab` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_cost_elements_2C_lab`(IN cel_tabl_name varchar(50),  
                                                                    IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('SELECT sum(cef.cost_2017) from
                        (SELECT t1.code_of_account,
                        CONCAT(t1.code_of_account,\'_lab\') as lab_name
                        FROM ', acc_tabl_name, ' AS t1
                        LEFT JOIN ', acc_tabl_name, ' as t2
                        ON t1.code_of_account = t2.supaccount
                        WHERE t2.code_of_account IS NULL
                        and t1.code_of_account!=\'2\'
                        and t1.code_of_account!=\'2C\' )as ac
                        join ', cel_tabl_name, ' as cef
                                on cef.cost_element = ac.lab_name
                                where ac.code_of_account!=\'2C\'');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_cost_elements_2C_mat` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_cost_elements_2C_mat`(IN cel_tabl_name varchar(50),
                                                                    IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('SELECT sum(cef.cost_2017) from
                        (SELECT t1.code_of_account,
                        CONCAT(t1.code_of_account,\'_mat\') as mat_name
                        FROM ', acc_tabl_name, ' AS t1
                        LEFT JOIN ', acc_tabl_name, ' as t2
                        ON t1.code_of_account = t2.supaccount
                        WHERE t2.code_of_account IS NULL
                        and t1.code_of_account!=\'2\'
                        and t1.code_of_account!=\'2C\' )as ac
                        join ', cel_tabl_name, ' as cef
                                on cef.cost_element = ac.mat_name
                                where ac.code_of_account!=\'2C\'');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_up_lmt_account_2C` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_up_lmt_account_2C`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT sum(t1.total_cost) as tc, sum(t1.prn) as tprn FROM
                            ', acc_tabl_name, ' AS t1 LEFT JOIN ', acc_tabl_name, ' as t2
                            ON t1.code_of_account = t2.supaccount
                            WHERE t2.code_of_account IS NULL
                            and t1.code_of_account!=\'2\'
                            and t1.code_of_account!=\'2C\') as dircost
                        SET ', acc_tabl_name, '.total_cost = dircost.tc,
                        ', acc_tabl_name, '.prn=dircost.tprn,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2C\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_up_lmt_direct_cost` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_up_lmt_direct_cost`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT  (total_cost/prn) as talcost
                            FROM ', acc_tabl_name, ' as pre_acc
                            WHERE pre_acc.code_of_account =\'2C\') as calcost
                        SET ', acc_tabl_name, '.total_cost = calcost.talcost,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sup_coa_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sup_coa_level`(IN table_name VARCHAR(50),
                                          IN supaccount VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT level FROM ', table_name, ' WHERE code_of_account = ?');
PREPARE stmt FROM @stmt;
SET @supaccount = supaccount;
EXECUTE stmt USING @supaccount;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_account_before_insert` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_account_before_insert`(IN table_name VARCHAR(50),
                                              IN min_ind INT)
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name,
                       ' SET ind = ind + 1 WHERE ind >?');
    PREPARE stmt FROM @stmt;
    SET @min_ind = min_ind;
    EXECUTE stmt USING @min_ind;
    DEALLOCATE PREPARE stmt;  
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_account_table_by_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_account_table_by_cost_elements`(IN acc_tabl_name varchar(50),
																					IN cel_tabl_name varchar(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
	SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
						'(SELECT ', acc_tabl_name, '.code_of_account,
								ce.total_cost as cost,
								ce.updated as updated
						FROM ', acc_tabl_name, '
						JOIN (SELECT account,
									sum(cost_2017) as total_cost,
									sum(updated) as updated
							FROM ', cel_tabl_name, '
							GROUP BY ', cel_tabl_name, '.account ) as ce
						on ', acc_tabl_name, '.code_of_account = ce.account
						ORDER BY ', acc_tabl_name, '.ind) as updated_account
						SET ', acc_tabl_name, '.total_cost = updated_account.cost,
						review_status = \'Ready for Review\'
						WHERE updated_account.updated > 0
						and ', acc_tabl_name, '.code_of_account = updated_account.code_of_account;');
	PREPARE stmt FROM @stmt;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_cost_element_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_cost_element_on_name`(IN table_name VARCHAR(50),
                                                                          IN `ce_name` VARCHAR(50),
                                                                          IN `alg_value` DECIMAL(20,5)  )
BEGIN
    SET SQL_SAFE_UPDATES = 0;

    SET @stmt = CONCAT('UPDATE ', table_name, 
                       ' SET cost_2017 = ', alg_value, 
                       ', updated = 1 WHERE cost_element = ''', ce_name, '''');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_new_accounts` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_new_accounts`(IN acc_tabl_name VARCHAR(50),
                                                                        IN var_tabl_name VARCHAR(50),
                                                                        IN alg_tabl_name VARCHAR(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT("SELECT ac.ind, ac.code_of_account,
       ac.total_cost, ac.alg_name,
       ac.variables, 
       alg.alg_python, alg.alg_formulation, alg.alg_units 
		FROM ", acc_tabl_name, " AS ac 
		JOIN ", alg_tabl_name, " AS alg ON ac.alg_name = alg.alg_name
		WHERE EXISTS (
			SELECT 1
			FROM ", var_tabl_name, " AS va
			WHERE va.user_input = 1
			AND FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0);");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_new_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_new_cost_elements`(IN cel_tabl_name VARCHAR(50),
                                                                        IN var_tabl_name VARCHAR(50),
                                                                        IN alg_tabl_name VARCHAR(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT("SELECT ce.ind, ce.cost_element,
       ce.cost_2017, ce.alg_name,
       ce.variables, ce.algno,
       alg.alg_python, alg.alg_formulation, alg.alg_units 
		FROM ", cel_tabl_name, " AS ce 
		JOIN ", alg_tabl_name, " AS alg ON ce.alg_name = alg.alg_name
		WHERE EXISTS (
			SELECT 1
			FROM ", var_tabl_name, " AS va
			WHERE va.user_input = 1
			AND FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0);");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_super_variable` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_super_variable`(IN var_table_name VARCHAR(50),
                            IN alg_table_name VARCHAR(50), IN `u_i_var_name` VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var.ind, var.var_name, var.var_value,
                        var.var_alg, var.var_need, alg.ind, alg.alg_python,
                        alg.alg_formulation, alg.alg_units, var.var_unit
                        FROM ', var_table_name, ' as var JOIN ', alg_table_name, ' as alg
                        ON var.var_alg=alg.alg_name
                        WHERE var.var_name=?');
PREPARE stmt FROM @stmt;
SET @var_name = u_i_var_name;
EXECUTE stmt USING @var_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_total_cost_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_total_cost_on_name`(IN table_name VARCHAR(50),
                                                                        IN `tc_id` VARCHAR(50), 
                                                                        IN `u_i_tc_value` DECIMAL(20,5))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name, ' SET total_cost = ?, 
                                              review_status = "User Input" WHERE code_of_account = ?');
    PREPARE stmt FROM @stmt;
    SET @tc_id = tc_id;
    SET @u_i_tc_value = u_i_tc_value;
    EXECUTE stmt USING @u_i_tc_value, @tc_id;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_variable_info_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_variable_info_on_name`(IN table_name VARCHAR(50),
                            IN `u_i_var_name` VARCHAR(50), IN `value` DECIMAL(20,5), IN `unit` VARCHAR(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name, ' SET var_value = ?,
                        var_unit = ?,
                        user_input = ? WHERE var_name = ?');
PREPARE stmt FROM @stmt;
SET @var_value = value;
SET @var_unit = unit;
SET @user_input = 1;
SET @var_name = u_i_var_name;
EXECUTE stmt USING @var_value, @var_unit, @user_input, @var_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-26 13:08:24
