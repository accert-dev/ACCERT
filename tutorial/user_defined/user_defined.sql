CREATE DATABASE  IF NOT EXISTS `accert_db`;
USE `accert_db`;

DROP TABLE IF EXISTS `user_defined_account`;
CREATE TABLE `user_defined_account` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `user_defined_account` WRITE;
INSERT INTO `user_defined_account` VALUES (1,'2','User defined direct cost',1000000000,0,'','Unchanged',1,'','',''),(2,'21','User defined total cost 21',700000000,1,'2','Unchanged',0.7,'','',''),(3,'211','User defined total cost 211',100000000,2,'21','Unchanged',0.1,'ud211','million','v1, v2, v3'),(4,'212','User defined total cost 212',200000000,2,'21','Unchanged',0.2,'ud212','dollar','v5, v8, v7'),(5,'213','User defined total cost 213',400000000,2,'21','Unchanged',0.4,'','',''),(7,'2131','User defined total cost 2131',150000000,3,'213','Unchanged',0.15,'ud2131','optional input','v3, v2, v5'),(8,'2132','User defined total cost 27',250000000,3,'213','Unchanged',0.25,'ud2132','million','v8, v4, v6'),(9,'22','example account without algorithm',300000000,1,'2','Unchanged',0.3,'','','');
UNLOCK TABLES;

DROP TABLE IF EXISTS `user_defined_algorithm`;
CREATE TABLE `user_defined_algorithm` (
  `ind` int DEFAULT NULL,
  `alg_name` varchar(50) NOT NULL,
  `alg_for` text,
  `alg_description` text,
  `alg_python` text,
  `alg_formulation` text,
  `alg_units` text,
  PRIMARY KEY (`alg_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `user_defined_algorithm` WRITE;
INSERT INTO `user_defined_algorithm` VALUES (5,'ud_cal_v6','v','description of  ud_cal_v6 optional','user_defined_func','formulation of  ud_cal_v6 optional','million'),(1,'ud211','c','description of  ud211 optional','user_defined_func','formulation of  ud211 optional','million'),(2,'ud212','c','description of  ud212 optional','user_defined_func','formulation of  ud212 optional','dollar'),(3,'ud2131','c','description of  ud2131 optional','user_defined_func','formulation of  ud2131 optional','million'),(4,'ud2132','c','description of  ud2132 optional','user_defined_func','formulation of  ud2132 optional','million');
UNLOCK TABLES;

DROP TABLE IF EXISTS `user_defined_variable`;

CREATE TABLE `user_defined_variable` (
  `ind` int DEFAULT NULL,
  `var_name` varchar(20) NOT NULL,
  `var_description` text,
  `var_value` double DEFAULT NULL,
  `var_unit` text,
  `var_alg` text,
  `var_need` text,
  `v_linked` text,
  `user_input` int DEFAULT NULL,
  PRIMARY KEY (`var_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `user_defined_variable` WRITE;
INSERT INTO `user_defined_variable` VALUES (1,'v1','description of  v1 optional',20,'million','','','v6',0),(2,'v2','description of  v2 optional',50,'million','','','',0),(3,'v3','description of  v3 optional',30,'million','','','v6',0),(4,'v4','description of  v4 optional',2.5,'km','','','',0),(5,'v5','description of  v5 optional',1500,'m','','','',0),(6,'v6','description of  v6 optional',50,'million','ud_cal_v6','v1, v3','',0),(7,'v7','description of  v7 optional',50000000,'dollar','','','',0),(8,'v8','description of  v8 optional',100000,'$/m','','','',0);
UNLOCK TABLES;
