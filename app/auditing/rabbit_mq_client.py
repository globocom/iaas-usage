import pika
from app import app


class RabbitMQClient:

    QUEUE_NAME = app.config['EVENT_QUEUE_NAME']
    ROUTING_KEY = app.config['EVENT_ROUTING_KEY_TEMPLATE']
    QUEUE_EXCHANGE = app.config['EVENT_QUEUE_EXCHANGE']
    QUEUE_HOST = app.config['EVENT_QUEUE_HOST']

    def __init__(self):
        self.channel = pika.BlockingConnection(pika.ConnectionParameters(host=self.QUEUE_HOST)).channel()

    def start_consuming(self, insert_function):
        queue_state = self.channel.queue_declare(queue=self.QUEUE_NAME)
        self._bind_queue()

        while queue_state.method.message_count > 0:
            self._read_message(insert_function)
        self.channel.close()

    def _bind_queue(self):
        for event_key in app.config['EVENT_LIST']:
            routing_key = self.ROUTING_KEY % event_key
            self.channel.queue_bind(exchange=self.QUEUE_EXCHANGE, queue=self.QUEUE_NAME, routing_key=routing_key)

    def _read_message(self, insert_function):
        method, properties, body = self.channel.basic_get(self.QUEUE_NAME)
        try:
            if method:
                if body and method.NAME == 'Basic.GetOk':
                    insert_function(body)
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception, e:
            print e.message
            app.logger.exception("error")  # TODO: tratar erros
