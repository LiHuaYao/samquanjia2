CREATE DATABASE IF NOT EXISTS m2u DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
use m2u;
CREATE TABLE `order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_no` varchar(64) NOT NULL DEFAULT '',
  `action_code` int(11) DEFAULT '0',
  `action_msg` varchar(64) DEFAULT '',
  `action_type` varchar(32) DEFAULT '',
  `status` smallint(6) NOT NULL COMMENT '0-未处理，1处理中，2-完成，3-失败',
  `bank_type` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4;