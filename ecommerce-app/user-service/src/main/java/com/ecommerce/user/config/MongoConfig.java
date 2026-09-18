package com.ecommerce.user.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

/**
 * How the MongoDB connection works:
 *
 * 1. Spring Boot reads  spring.data.mongodb.uri  from application.properties
 * 2. It auto-creates a  MongoClient  (connection pool to MongoDB)
 * 3. MongoTemplate uses that client to run queries
 * 4. UserRepository (extends MongoRepository) gets a generated implementation
 *    that delegates every findBy / save / delete call to MongoTemplate
 *
 * Connection flow:
 *   UserController → UserService → UserRepository → MongoTemplate → MongoClient → MongoDB
 */
@Configuration
@EnableMongoRepositories(basePackages = "com.ecommerce.user.repository")
public class MongoConfig {

    private static final Logger log = LoggerFactory.getLogger(MongoConfig.class);

    @Value("${spring.data.mongodb.uri}")
    private String mongoUri;

    /**
     * Runs once at startup to verify the MongoDB connection.
     * Logs the database name and current document count so you can
     * confirm the service is actually talking to the right database.
     */
    @Bean
    public CommandLineRunner verifyMongoConnection(MongoTemplate mongoTemplate) {
        return args -> {
            try {
                // Ping verifies the TCP connection to MongoDB is alive
                mongoTemplate.executeCommand("{ ping: 1 }");

                long count = mongoTemplate.getCollection("users").countDocuments();

                log.info("╔══════════════════════════════════════════╗");
                log.info("║  USER-SERVICE  →  MongoDB                ║");
                log.info("╠══════════════════════════════════════════╣");
                log.info("║  Status   : CONNECTED                    ║");
                log.info("║  Database : {}  ║", mongoTemplate.getDb().getName());
                log.info("║  Users    : {} document(s) in collection ║", count);
                log.info("║  URI      : {}... ║", mongoUri.substring(0, Math.min(mongoUri.length(), 30)));
                log.info("╚══════════════════════════════════════════╝");
            } catch (Exception e) {
                log.error("╔══════════════════════════════════════════╗");
                log.error("║  USER-SERVICE  →  MongoDB FAILED         ║");
                log.error("║  Error: {}  ║", e.getMessage());
                log.error("╚══════════════════════════════════════════╝");
            }
        };
    }
}
