# elasticsearch-aggregations
Elasticsearch aggregations.

# Deploy with docker-compose
```
cd deploy
docker-compose up -d
cd -
```

Note: please go to `Useful commands` if needed.

# Static schema

Elasticsearch is able of indexing documents event without knowing the schema (dynamic mappins).
For better optimization and index speed static schema with proper field types is recommended.
Sample schema:
```json
PUT /beers
{
  "mappings": {
	  "dynamic": false,
	  "properties" : {
	    "name" : {
	      "type" : "text"
	    },
	    "country" : {
	      "type" : "keyword"
	    },
	    "price": {
	      "type": "float"
	    },
	    "city": {
	      "type": "keyword"
	    },
	    "name_breweries": {
	      "type": "text"
	    }
	  }
	}
}
```

# Load data
Requirements: python.
```
cd dataset
python load_beers.py
cd -
```

# Query context (relevance score)
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "match": {
      "name":"Porter"
    }
  }
}
```

# Filter context (yes or no)
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "bool": {
        "must": [
          { "match_all": {} }
        ],
      "filter": [
        {"term": {"country":"Poland"}}
      ]
    }
  }
}
```

# Stats
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-stats-aggregation.html)
```json
POST /INDEX_NAME/_search?size=0
{
    "size": 0,
    "aggs" : {
        "price_stats" : { 
          "stats" : { 
            "field" : "price" 
          } 
        }
    }
}
```

# Percentiles
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-percentile-aggregation.html)
```json
POST /INDEX_NAME/_search
{
    "size": 0,
    "aggs" : {
        "price_buckets" : {
            "percentiles" : {
                "field" : "price",
                "percents" : [20, 40, 60, 80],
                "keyed": false
            }
        }
    }
}
```

# Buckets
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket.html)

- terms (create buckets for all unique values of field)
```json
POST /INDEX_NAME/_search
{
    "size": 0,
    "aggs" : {
        "country_beers" : { 
          "terms" : { 
            "field" : "country" 
          } 
        }
    }
}
```

- filters (create bucket for each defined filter)
```json
POST /INDEX_NAME/_search
{
    "size": 0,
    "aggs" : {
        "country_beers" : {
        	"filters" : {
        		"filters" : {
        			"Austria": { "match" : {  "country" : "Austria" } },
        			"Czech": { "match" : {  "country" : "Czech Republic" } },
        			"Germany": { "match" : {  "country" : "Germany" } },
        			"Hungary": { "match" : {  "country" : "Hungary" } },
	        		"Poland": { "match" : {  "country" : "Poland" } }
        		}
        	}	
        }
    }
}
```

# Nested
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-nested-aggregation.html)

```json
POST /INDEX_NAME/_search
{
    "size": 0,
    "aggs" : {
        "country_beers" : {
        	"filters" : {
        		"filters" : {
        			"Austria": { "match" : {  "country" : "Austria" } },
        			"Czech": { "match" : {  "country" : "Czech Republic" } },
        			"Germany": { "match" : {  "country" : "Germany" } }
        		}
        	},
        	"aggs" : {
        		"price_stats" : { 
		          "stats" : { 
		            "field" : "price" 
		          }
		        }
        	}
        }
    }
}
```

# Useful commands

- get indices
```
GET http://localhost:9200/_cat/indices?v
```
- index description
```
GET http://localhost:9200/beers
```

