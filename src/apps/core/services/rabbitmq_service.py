# messaging/rabbitmq.py
import pika
import json
from django.conf import settings


class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ"""
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,  # Keep connection alive
            blocked_connection_timeout=300,
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare a durable queue (survives broker restart)
        self.channel.queue_declare(queue="mobile_tasks", durable=True)

    def publish_message(self, queue_name, message):
        """Send a message to the specified queue"""
        if not self.channel:
            self.connect()

        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type="application/json",
            ),
        )

    def close(self):
        """Clean up connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


def rabbitmq_publish_message(user):
    producer = RabbitMQProducer()
    try:
        producer.publish_message(
            "mobile_tasks",
            {
                "type": "welcome_mobile",
                "user_id": user.id,
                "mobile": user.mobile,
                "username": user.username,
            },
        )
    finally:
        producer.close()
