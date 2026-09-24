from prometheus_client import Counter, Gauge

MESSAGES_SENT = Counter("chat_messages_total", "Chat messages sent", ["room"])
CONNECTED_USERS = Gauge("chat_connected_clients", "Currently connected socket clients")
HTTP_REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "endpoint", "status"])
