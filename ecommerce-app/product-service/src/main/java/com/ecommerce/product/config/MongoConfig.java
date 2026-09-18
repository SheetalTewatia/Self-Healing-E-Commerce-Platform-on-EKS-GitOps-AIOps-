package com.ecommerce.product.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

/**
 * How MongoDB connection works in product-service:
 *
 * application.properties → spring.data.mongodb.uri
 *   ↓
 * Spring Boot auto-configures MongoClient (connection pool, max 100 connections)
 *   ↓
 * MongoTemplate wraps the client — executes find/insert/update/delete
 *   ↓
 * ProductRepository (interface) — Spring generates the implementation at startup
 *   findAll()        → db.products.find({})
 *   findByCategory() → db.products.find({ category: "Electronics" })
 *   save(product)    → db.products.insertOne(product) or updateOne
 *   deleteById(id)   → db.products.deleteOne({ _id: ObjectId(id) })
 */
@Configuration
@EnableMongoRepositories(basePackages = "com.ecommerce.product.repository")
public class MongoConfig {

    private static final Logger log = LoggerFactory.getLogger(MongoConfig.class);

    @Value("${spring.data.mongodb.uri}")
    private String mongoUri;

    @Bean
    public CommandLineRunner verifyMongoConnection(MongoTemplate mongoTemplate) {
        return args -> {
            try {
                mongoTemplate.executeCommand("{ ping: 1 }");
                long count = mongoTemplate.getCollection("products").countDocuments();

                log.info("╔══════════════════════════════════════════╗");
                log.info("║  PRODUCT-SERVICE  →  MongoDB             ║");
                log.info("╠══════════════════════════════════════════╣");
                log.info("║  Status   : CONNECTED                    ║");
                log.info("║  Database : {}   ║", mongoTemplate.getDb().getName());
                log.info("║  Products : {} document(s) in collection ║", count);
                log.info("╚══════════════════════════════════════════╝");
            } catch (Exception e) {
                log.error("║  PRODUCT-SERVICE  →  MongoDB FAILED: {}  ║", e.getMessage());
            }
        };
    }
}
