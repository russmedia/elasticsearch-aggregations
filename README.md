# elasticsearch-aggregations
Elasticsearch aggregations.

Table of contents
=================

   * [Deploy with docker-compose](#deploy)
   * [Table of contents](#table-of-contents)
      * [1. Static schema](#1-static-schema)
      * [2. Load data](#2-load-data)
      * [3. Query context](#3.-query-context)
      * [4. Filter context](#4.-filter-context)
      * [5. Aggregations](#5.-aggregations)
        * [5.1. Stats](#5.1.-stats)
        * [5.2. Percentiles](#5.2.-percentiles)
        * [5.3. Buckets](#5.3.-buckets)
        * [5.4. Nested](#5.4.-nested)
      * [6. Advanced full-text search](#6.-advanced)
        * [6.1. Proximity search](#6.1.-proximity-search)
        * [6.2. Fuzzyness](#6.2.-fuzzyness)
      * [7. Useful commands](#7.-useful-commands)

## Deploy with docker-compose
```
cd deploy
docker-compose up -d
cd -
```

Note: please go to `Useful commands` if needed.

## 1. Static schema

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

## 2. Load data
Requirements: python.
```
cd dataset
python load_beers.py
cd -
```

## 3. Query context (relevance score)
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

## 4. Filter context (yes or no)
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

## 5. Aggregations

### 5.1. Stats
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

### 5.2. Percentiles
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

### 5.3. Buckets
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

### 5.4. Nested
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

## 6. Advanced full-text search
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html)

### 6.1. Proximity search

- look for phrase with specific words and order
```json
POST /INDEX_NAME/_search
{
  "query": {
    "match_phrase": {
      "name_breweries":{
      	"query": "Zywiec Browar",
    	"slop": 2
      }
    }
  }
}
```

### 6.2. Fuzzyness
- fix misspelling 
- fuzziness describe how many character chnages per word can be made
- degrades performance
```json
POST /INDEX_NAME/_search
{
  "query": {
    "match": {
      "name_breweries":{
      	"query": "ZywiecX",
    	"fuzziness": 1
      }
    }
  }
}
```

## 7. Useful commands

- get indices
```
GET http://localhost:9200/_cat/indices?v
```
- index description
```
GET http://localhost:9200/beers
```
