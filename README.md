# Rabbit Facet Indexer

This provides the code to read from the rabbit queue and process updates
to the files index, adding facets.

Watched events:
- DEPOSIT

Exposed Queue Consumer Classes:
- `rabbit_facet_indexer.queue_consumers.FacetScannerQueueConsumer`

## Configuration

Configuration is handled using a YAML file. The full configuration options 
are described in the [rabbit_indexer repo](https://github.com/cedadev/rabbit-index-ingest/blob/master/README.md#rabbit_event_indexer)

This process also requires an environment variable `JSON_TAGGER_ROOT`. This should be set to
the `json` directory which contains the tagging json.

The required sections for the facet indexer are:
- rabbit_server
- indexer
- logging
- moles
- elasticsearch
- files_index

An example YAML file (secrets noted by ***** ): 

```yaml

---
rabbit_server:
  name: "*****"
  user: "*****"
  password: "*****"
  vhost: "*****"
  source_exchange:
    name: deposit_logs
    type: fanout
  dest_exchange:
    name: fbi_fanout
    type: fanout
  queues:
    - name: elasticsearch_update_queue_opensearch_tags_test
      kwargs:
        auto_delete: false
    - name: elasticsearch_update_queue_opensearch_tags_test
      bind_kwargs:
        routing_key: opensearch.tagger.cci
indexer:
  queue_consumer_class: rabbit_facet_indexer.queue_consumers.FacetScannerQueueConsumer
  path_filter:
    paths:
      - /neodc/esacci
    filter_policy: 2
logging:
  log_level: info
moles:
  moles_obs_map_url: http://api.catalogue.ceda.ac.uk/api/v2/observations.json/?publicationState__in=citable,published,preview,removed&fields=publicationState,result_field,title,uuid
elasticsearch:
  es_api_key: "*****"
files_index:
  name: ceda-fbi
  calculate_md5: false
  scan_level: 2
```

## Running

The indexer can be run using the helper script provided by [rabbit_indexer repo](https://github.com/cedadev/rabbit-index-ingest/blob/master/README.md#configuration).
This uses an entry script and parses the config file to run your selected queue_consumer_class: 

`rabbit_event_indexer --conf <path_to_configuration_file>`