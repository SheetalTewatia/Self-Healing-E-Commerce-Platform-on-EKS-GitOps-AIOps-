package com.ecommerce.order.service;

import com.ecommerce.order.model.Order;
import com.ecommerce.order.model.OrderItem;
import com.ecommerce.order.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;

@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final RestTemplate restTemplate;

    @Value("${product.service.url:http://localhost:8082}")
    private String productServiceUrl;

    @Value("${notification.service.url:http://localhost:8084}")
    private String notificationServiceUrl;

    public OrderService(OrderRepository orderRepository, RestTemplate restTemplate) {
        this.orderRepository = orderRepository;
        this.restTemplate = restTemplate;
    }

    public Order placeOrder(String userId, String userName, List<Map<String, Object>> cartItems) {
        List<OrderItem> orderItems = new ArrayList<>();
        double total = 0;

        for (Map<String, Object> item : cartItems) {
            String productId = (String) item.get("productId");
            int quantity = (Integer) item.get("quantity");

            // Call Product Service to get product details
            @SuppressWarnings("unchecked")
            Map<String, Object> product = restTemplate.getForObject(
                productServiceUrl + "/api/products/" + productId, Map.class);

            if (product == null) throw new RuntimeException("Product not found: " + productId);

            String productName = (String) product.get("name");
            double price = ((Number) product.get("price")).doubleValue();

            // Call Product Service to reduce stock
            restTemplate.put(productServiceUrl + "/api/products/" + productId + "/stock/reduce",
                Map.of("quantity", quantity));

            orderItems.add(new OrderItem(productId, productName, quantity, price));
            total += price * quantity;
        }

        Order order = new Order();
        order.setUserId(userId);
        order.setUserName(userName);
        order.setItems(orderItems);
        order.setTotal(Math.round(total * 100.0) / 100.0);
        order.setStatus("PLACED");

        Order saved = orderRepository.save(order);

        // Call Notification Service to notify the user
        try {
            restTemplate.postForObject(notificationServiceUrl + "/api/notifications",
                Map.of("userId", userId, "message",
                    "Your order #" + saved.getId().substring(0, 8) + " has been placed! Total: $" + saved.getTotal(),
                    "type", "ORDER"),
                Map.class);
        } catch (Exception ignored) {
            // Notification failure should not fail the order
        }

        return saved;
    }

    public List<Order> getOrdersByUser(String userId) {
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    public Optional<Order> getOrderById(String id) {
        return orderRepository.findById(id);
    }
}
