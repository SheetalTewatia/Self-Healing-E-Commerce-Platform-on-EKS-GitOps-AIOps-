package com.ecommerce.notification.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

@Configuration
@EnableMongoRepositories(basePackages = "com.ecommerce.notification.repository")
public class MongoConfig {

    private static final Logger log = LoggerFactory.getLogger(MongoConfig.class);

    @Value("${spring.data.mongodb.uri}")
    private String mongoUri;

    @Bean
    public CommandLineRunner verifyMongoConnection(MongoTemplate mongoTemplate) {
        return args -> {
            try {
                mongoTemplate.executeCommand("{ ping: 1 }");
                long count = mongoTemplate.getCollection("notifications").countDocuments();

                log.info("╔══════════════════════════════════════════╗");
                log.info("║  NOTIFICATION-SERVICE  →  MongoDB        ║");
                log.info("╠══════════════════════════════════════════╣");
                log.info("║  Status        : CONNECTED               ║");
                log.info("║  Database      : {}  ║", mongoTemplate.getDb().getName());
                log.info("║  Notifications : {} document(s)          ║", count);
                log.info("╚══════════════════════════════════════════╝");
            } catch (Exception e) {
                log.error("║  NOTIFICATION-SERVICE  →  MongoDB FAILED: {} ║", e.getMessage());
            }
        };
    }
}
