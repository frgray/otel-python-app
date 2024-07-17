CREATE TABLE `users` (
                         `id` int(11) NOT NULL AUTO_INCREMENT,
                         `email` varchar(255) COLLATE utf8_bin NOT NULL,
                         `firstName` varchar(255) COLLATE utf8_bin NOT NULL,
                         `lastName` varchar(255) COLLATE utf8_bin NOT NULL,
                         PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  AUTO_INCREMENT=1 ;