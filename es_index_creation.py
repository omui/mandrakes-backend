from elasticsearch import Elasticsearch
es = Elasticsearch(['10.150.154.107:9200'])

mapping_ticket = {
    "mappings": {
        "_doc": {
            "properties": {
                "id": {
                    "type": "keyword"
                    },
                "uuid": {
                    "type": "keyword"
                    },
                "title": {
                    "type": "keyword"
                    },
                "content": {
                    "type": "text"
                    },
                "creation_date": {
                    "type": "long"
                    },
                "context": {
                    "type": "keyword"
                    },
                "data": {
                    "type": "text"
                    },
                "status": {
                    "type": "integer"
                    },
                "response": {
                    "type": "text"
                    },
                "resolution_date": {
                    "type": "long"
                    },
                "lastStatusUpdate_date": {
                    "type": "long"
                    }
            }
        }
    }
}

if es.indices.exists('hackathon_ticket') == False:
    es.indices.create(index= 'hackathon_ticket', body= mapping_ticket)
else:
    pass