# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '19 Feb 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# Local imports
from rabbit_indexer.index_updaters.base import UpdateHandler
from rabbit_indexer.utils import PathTools

# Third-party
from facet_scanner.core.facet_scanner import FacetScanner
from ceda_elasticsearch_tools.elasticsearch import CEDAElasticsearchClient

# Typing imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rabbit_indexer.queue_handler.queue_handler import IngestMessage


class FacetScannerUpdateHandler(UpdateHandler):

    def setup_extra(self, **kwargs) -> None:
        """
        Setup the facet scanner class and elasticserach connection to

        :param kwargs:
        """
        # Get the facet scanner class
        self.facet_scanner = FacetScanner()

        # Set up the Elasticsearch connection
        api_key = self.conf.get('elasticsearch', 'es-api-key')
        self.index = self.conf.get('files_index', 'name')

        self.es = CEDAElasticsearchClient(headers={'x-api-key': api_key})

    def process_event(self, message: 'IngestMessage'):
        """
        Scan the file for facets
        :param message:
        :return:
        """

        if message.action == 'DEPOSIT':
            self._process_deposits(message)

    def _process_deposits(self, message: 'IngestMessage'):

        # Wait to make sure that the file is accessible on the filesystem
        self._wait_for_file(message)

        # Get the handler for this filepath
        handler = self.facet_scanner.get_handler(message.filepath)

        # Extract the facets
        facets = handler.get_facets(message.filepath)

        # Build the project dictionary using the handlers project name attr
        project = {
            'projects': {
                handler.project_name: facets
            }
        }

        # Send facets to elasticsearch
        self.es.update(
            index=self.index,
            id=PathTools.generate_id(message.filepath),
            body={'doc': project, 'doc_as_upsert': True}
        )
