from locust import HttpUser, task, between, tag
import random
import uuid

# --- Helper functions to create payloads ----------------------------------


def random_items():
    product_ids = ["p1", "p2", "p3"]
    return [
        {
            "product_id": random.choice(product_ids),
            "quantity": random.randint(1, 3),
        }
        for _ in range(random.randint(1, 3))
    ]


def make_checkout_payload():
    return {
        "user_id": str(uuid.uuid4()),
        "payment_method": random.choice(["credit_card", "paypal"]),
        "items": random_items(),
    }


def make_payment_payload():
    return {
        "user_id": str(uuid.uuid4()),
        "amount": random.uniform(5.0, 100.0),
        "method": random.choice(["credit_card", "paypal"]),
    }


def make_inventory_payload():
    return {"items": random_items()}


def make_notification_payload():
    return {
        "order_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
    }


# --- 1. Full system test via API Gateway ----------------------------------


class GatewayUser(HttpUser):
    """
    Simulates real clients going through the API Gateway.
    This exercises gateway -> order -> inventory + payment + notification.
    """
    host = "http://localhost:8000"  # api_gateway
    wait_time = between(0.1, 1.0)

    @tag("gateway")
    @task
    def checkout(self):
        payload = make_checkout_payload()
        self.client.post("/checkout", json=payload, name="gateway_checkout")


# --- 2. Direct tests on Order Service -------------------------------------


class OrderServiceUser(HttpUser):
    """
    Directly calls the order-service. This isolates order-service behaviour
    from gateway overhead if you run it alone.
    """
    host = "http://localhost:8001"  # order_service
    wait_time = between(0.1, 1.0)

    @tag("order")
    @task
    def create_order(self):
        payload = make_checkout_payload()
        self.client.post("/orders", json=payload, name="order_create")


# --- 3. Direct tests on Payment Service -----------------------------------


class PaymentServiceUser(HttpUser):
    """
    Directly calls the payment-service. Good for measuring factory-based
    provider selection in isolation.
    """
    host = "http://localhost:8002"  # payment_service
    wait_time = between(0.1, 1.0)

    @tag("payment")
    @task
    def charge(self):
        payload = make_payment_payload()
        self.client.post("/charge", json=payload, name="payment_charge")


# --- 4. Direct tests on Inventory Service ---------------------------------


class InventoryServiceUser(HttpUser):
    """
    Directly calls the inventory-service. Lets you see how pricing / stock
    logic behaves under high read load.
    """
    host = "http://localhost:8003"  # inventory_service
    wait_time = between(0.1, 1.0)

    @tag("inventory")
    @task
    def check_inventory(self):
        payload = make_inventory_payload()
        self.client.post("/check", json=payload, name="inventory_check")


# --- 5. Direct tests on Notification Service ------------------------------


class NotificationServiceUser(HttpUser):
    """
    Directly calls the notification-service. In the real system it is
    invoked by order-service, but here we can hammer it directly.
    """
    host = "http://localhost:8004"  # notification_service
    wait_time = between(0.2, 1.5)

    @tag("notification")
    @task
    def send_notification(self):
        payload = make_notification_payload()
        self.client.post("/order-created",
                         json=payload,
                         name="notification_order_created")
