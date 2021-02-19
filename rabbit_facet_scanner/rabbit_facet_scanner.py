# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '17 Feb 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from rabbit_facet_scanner.handlers.facet_scanner_handler import FacetScannerUpdateHandler

from rabbit_indexer.queue_handler import QueueHandler
from rabbit_indexer.utils.consumer_setup import consumer_setup

import logging

logger = logging.getLogger(__name__)


class FacetScannerQueueConsumer(QueueHandler):
    """
    RabbitMQ queue consumer to extract facets from the CEDA Archive for faceted search
    """

    def get_handlers(self):

        self.queue_handler = FacetScannerUpdateHandler(conf=self.conf)

    def callback(self, ch, method, properties, body, connection):
        """
        Callback to run during basic consume routine.
        Arguments provided by pika standard message callback method

        :param ch: Channel
        :param method: pika method
        :param properties: pika header properties
        :param body: Message body
        :param connection: Pika connection
        """

        try:
            message = self.decode_message(body)

        except IndexError:
            # Acknowledge message if the message is not compliant
            self.acknowledge_message(ch, method.delivery_tag, connection)
            return

        # Filter by path for specific project
        if not message.filepath.startswith('/neodc/esacci'):
            self.acknowledge_message(ch, method.delivery_tag, connection)
            return

        # Try to extract the facet tags
        try:
            if message.action in ['DEPOSIT']:
                self.queue_handler.process_event(message)

            # Acknowledge message
            self.acknowledge_message(ch, method.delivery_tag, connection)

        except Exception as e:
            # Catch all exceptions in the scanning code and log them
            logger.error(f'Error occurred while scanning: {message}', exc_info=e)
            raise


def main():
    consumer_setup(FacetScannerQueueConsumer ,logger)


if __name__ == '__main__':
    main()