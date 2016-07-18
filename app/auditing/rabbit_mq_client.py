import pika
from app import app


class RabbitMQClient(object):

    QUEUE_NAME = app.config['EVENT_QUEUE_NAME']
    QUEUE_ROUTING_KEY = app.config['EVENT_ROUTING_KEY_TEMPLATE']
    QUEUE_EXCHANGE = app.config['EVENT_QUEUE_EXCHANGE']
    QUEUE_HOST = app.config['EVENT_QUEUE_HOST']
    QUEUE_USER = app.config['EVENT_QUEUE_USER']
    QUEUE_PASSWORD = app.config['EVENT_QUEUE_PASSWORD']

    def __init__(self):
        credentials = pika.PlainCredentials(self.QUEUE_USER, self.QUEUE_PASSWORD)
        connection_parameters = pika.ConnectionParameters(host=self.QUEUE_HOST, credentials=credentials)
        self.channel = pika.BlockingConnection(connection_parameters).channel()

    def start_consuming(self, insert_function):
        queue_state = self.channel.queue_declare(queue=self.QUEUE_NAME)
        self._bind_queue()

        while queue_state.method.message_count > 0:
            self._read_message(insert_function)
            queue_state = self.channel.queue_declare(queue=self.QUEUE_NAME, passive=True)
        self.channel.close()

    def _bind_queue(self):
        for event_key in app.config['EVENT_LIST']:
            routing_key = self.QUEUE_ROUTING_KEY % event_key
            self.channel.queue_bind(exchange=self.QUEUE_EXCHANGE, queue=self.QUEUE_NAME, routing_key=routing_key)

    def _read_message(self, insert_function):
        method, properties, body = self.channel.basic_get(self.QUEUE_NAME)
        try:
            if body and method.NAME == 'Basic.GetOk':
                insert_function(body)
            self.channel.basic_ack(delivery_tag=method.delivery_tag)
        except:
            app.logger.exception("Error while reading event")
