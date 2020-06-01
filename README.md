# elasticsearch-aggregations
Elasticsearch aggregations.

Table of contents
=================

   * [Table of contents](#table-of-contents)
      * [Deploy](#deploy)
      * [1. Static schema](#1-static-schema)
      * [2. Load data](#2-load-data)
      * [3. Query context](#3-query-context)
      * [4. Filter context](#4-filter-context)
      * [5. Aggregations](#5-aggregations)
        * [Stats](#stats)
        * [Percentiles](#percentiles)
        * [Buckets](#buckets)
        * [Nested](#nested)
      * [6. Advanced fulltext search](#6-advanced-fulltext-search)
        * [Proximity search](#proximity-search)
        * [Fuzzyness](#fuzzyness)
        * [Query boost](#query-boost)
        * [Geo search](#geo-search)
      * [7. Synonyms](#7-synonyms)
      * [8. Useful commands](#8-useful-commands)

## Deploy
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
      },
      "coordinates": {
        "type": "geo_point"
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

## 3. Query context
(relevance score explanation)
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
 and now expaine the query chnaging URL:
 `http://localhost:9200/beers/_explain/244c6b68f6c6768c721296c8bc023615ab6587af` (needs ID of first document from previous example)

## 4. Filter context
(yes or no)
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"country":"Poland"}}
      ]
    }
  }
}
```

## 5. Aggregations

### Stats
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-stats-aggregation.html)
```json
POST http://localhost:9200/beers/_search
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
Note: `stats` -> `extended_stats` == more statistical data

### Percentiles
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-percentile-aggregation.html)
```json
POST http://localhost:9200/beers/_search
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
Note: they are approximate - to be able to scale this solution.

### Buckets (aka faceting in Solr)
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket.html)

- terms (create buckets for all unique values of field)
```json
POST http://localhost:9200/beers/_search
{
    "size": 0,
    "aggs" : {
        "country_beers_bucket" : { 
          "terms" : { 
            "field" : "country",
            "size": 10
          } 
        },
        "city_beers_bucket" : {
          "terms" : { 
            "field" : "city",
            "size": 10
          } 
        }
    }
}
```

- buckets with narrow search (going into facet-like aggregation)
```
POST http://localhost:9200/beers/_search
{
    "size": 0,
    "query": {
	    "bool": {
	      "filter": [
	        {"term": {"country":"Germany"}}
	      ]
    }
	  },
    "aggs" : {
        "city_beers_bucket" : {
          "terms" : { 
            "field" : "city",
            "size": 10
          } 
        }
    }
}
```

- filters (create bucket for each defined filter)
```json
POST http://localhost:9200/beers/_search
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

### Nested
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-nested-aggregation.html)

```json
POST http://localhost:9200/beers/_search
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

## 6. Advanced fulltext search
[docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html)

### Proximity search

- normal query (with AND) - finding too many results
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "match_phrase": {
      "name_breweries":{
      	"query": "Zywiec Browar",
      	"operator": "AND"
    	
      }
    }
  }
}
```

- look for phrase with specific words and order
```json
POST http://localhost:9200/beers/_search
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

- search across multiple fields
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "multi_match" : {
      "query":    "Zywiec Browar", 
      "fields": [ "name_breweries", "name" ],
      "operator": "AND"
    }
  }
}
```

### Fuzzyness
- fix misspelling 
- fuzziness describe how many character chnages per word can be made
- degrades performance
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "match": {
      "name_breweries":{
      	"query": "ZywieX",
    	"fuzziness": 1
      }
    }
  }
}
```

### Query boost
```json
POST http://localhost:9200/beers/_search
{
  "query": {
    "bool" : {
      "must" : [
      		{
      			"match" : { 
      				"name" : 
	      			{
	      				"query": "Porter",
	      				"boost": 5    				
	      			}
      			}
      		},
      		{
      			"match": { "name_breweries": "Browar Zywiec"}
      		}
      ],
      "must_not": {
      	"term": { "country": "United States"}
      }
    }
  }
}
```
and go to explain (same body, just use below HTTP endpoint and method)
`GET http://localhost:9200/beers/_explain/244c6b68f6c6768c721296c8bc023615ab6587af`


### Geo-search

Note: loading geo-point from array is in different order!

- [geo-point](https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html)
- [geo-search](https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-queries.html)

- by rectangle (Berlin coordinates)
```json
POST http://localhost:9200/beers/_search
{
    "query": {
        "bool" : {
            "must" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_bounding_box" : {
                    "coordinates" : {
                        "top_left" : {
                            "lat" : 52.644465,
                            "lon" : 13.090329
                        },
                        "bottom_right" : {
                            "lat" : 52.304024,
                            "lon" : 13.732684
                        }
                    }
                }
            }
        }
    }
}
```

- by distance from point (Munich)
```json
POST http://localhost:9200/beers/_search
{
    "query": {
        "bool" : {
            "must" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_distance" : {
                    "distance" : "10km",
                    "coordinates" : {
                        "lat" : 48.135125,
                        "lon" : 11.569979
                    }
                }
            }
        }
    }
}
```

- by drawing a polygon (Bregenz - Schwarzach - Dornibirn)
```json
POST http://localhost:9200/beers/_search
{
    "query": {
        "bool" : {
            "must" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_polygon" : {
                    "coordinates" : {
                        "points" : [
                            {"lat" : 47.406177, "lon" : 9.745112},
                            {"lat" : 47.446801, "lon" : 9.762261},
                            {"lat" : 47.501465, "lon" : 9.731163}
                        ]
                    }
                }
            }
        }
    }
}
```
## 7. Synonyms

Sample for query time only (returns also Zywiec if Krakow is entered for brewery name):
- create synonym file:
```bash
docker cp deploy/synonyms.txt es01:/usr/share/elasticsearch/config/synonyms.txt
```
- create index with custom analyzer for `name_breweries` field
```json
PUT http://localhost:9200/beers2
{
  "settings": {
    "index": {
      "analysis": {
        "analyzer": {
          "synonym_analyzer": {
            "tokenizer": "whitespace",
            "filter": ["my_synonyms"]
          }
        },
        "filter": {
          "my_synonyms": {
            "type": "synonym",
            "synonyms_path": "synonyms.txt",
            "updateable": true
          }
        }
      }
    }
  },
  "mappings": {
	  "dynamic": false,
	  "properties" : {
	    "name" : {
	      "type" : "text"
	    },
	    "name_breweries": {
	      "type": "text",
	      "analyzer": "standard",
	      "search_analyzer": "synonym_analyzer"
      }
	  }
	}
}
```
- add data
```json
PUT http://localhost:9200/beers2/_doc/1
{
  "name": "Porter",
  "name_breweries": "Browar Zywiec" 
}
```
- search for Krakow (brewery with such name does not exists):
```json
POST http://localhost:9200/beers2/_search
{
  "query": {
    "match": {
      "name_breweries": "krakow"
    }
  }
}
```

## 8. Useful commands

- get indices
```
GET http://localhost:9200/_cat/indices?v
```
- index description
```
GET http://localhost:9200/beers
```

- get mapping
```
http://localhost:9200/beers/_mapping
```

- delete index
```
DELETE http://localhost:9200/beers
```
