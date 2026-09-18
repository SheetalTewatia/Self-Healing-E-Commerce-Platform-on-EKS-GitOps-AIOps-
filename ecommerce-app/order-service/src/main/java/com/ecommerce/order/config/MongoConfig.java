package com.ecommerce.order.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;
import org.springframework.web.client.RestTemplate;

/**
 * Order-service connects to THREE things:
 *
 *   1. MongoDB (orderdb)       — stores orders
 *   2. product-service:8082    — fetches product details + reduces stock
 *   3. notification-service:8084 — creates notification on order placed
 *
 * MongoDB flow:
 *   POST /api/orders → OrderController → OrderService
 *     → restTemplate.GET  product-service/api/products/{id}   (fetch product)
 *     → restTemplate.PUT  product-service/api/products/{id}/stock/reduce
 *     → orderRepository.save(order)  → MongoDB orderdb
 *     → restTemplate.POST notification-service/api/notifications
 */
@Configuration
@EnableMongoRepositories(basePackages = "com.ecommerce.order.repository")
public class MongoConfig {

    private static final Logger log = LoggerFactory.getLogger(MongoConfig.class);

    @Value("${spring.data.mongodb.uri}")
    private String mongoUri;

    @Value("${product.service.url:http://localhost:8082}")
    private String productServiceUrl;

    @Value("${notification.service.url:http://localhost:8084}")
    private String notificationServiceUrl;

    @Bean
    public CommandLineRunner verifyMongoConnection(MongoTemplate mongoTemplate) {
        return args -> {
            try {
                mongoTemplate.executeCommand("{ ping: 1 }");
                long count = mongoTemplate.getCollection("orders").countDocuments();

                log.info("╔══════════════════════════════════════════╗");
                log.info("║  ORDER-SERVICE  →  MongoDB               ║");
                log.info("╠══════════════════════════════════════════╣");
                log.info("║  Status         : CONNECTED              ║");
                log.info("║  Database       : {}        ║", mongoTemplate.getDb().getName());
                log.info("║  Orders         : {} document(s)         ║", count);
                log.info("║  product-svc    : {}  ║", productServiceUrl);
                log.info("║  notif-svc      : {}  ║", notificationServiceUrl);
                log.info("╚══════════════════════════════════════════╝");
            } catch (Exception e) {
                log.error("║  ORDER-SERVICE  →  MongoDB FAILED: {}   ║", e.getMessage());
            }
        };
    }
}
