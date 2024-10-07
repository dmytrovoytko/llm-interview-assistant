import os
from glob import glob
import pandas as pd
from dotenv import load_dotenv

try:
    from sentence_transformers import SentenceTransformer
    from elasticsearch import Elasticsearch
except:
    pass

import minsearch


load_dotenv()

USE_ELASTIC = os.getenv("USE_ELASTIC")
ELASTIC_URL = os.getenv("ELASTIC_URL") # ELASTIC_URL_LOCAL
INDEX_MODEL_NAME = os.getenv("INDEX_MODEL_NAME", "multi-qa-MiniLM-L6-cos-v1")
INDEX_NAME = os.getenv("INDEX_NAME")
DATA_PATH = os.getenv("DATA_PATH", "data")
BASE_URL = "https://github.com/dmytrovoytko/llm-interview-assistant/blob/main"

def fetch_documents(data_path=DATA_PATH):
    print("Fetching documents...")
    # # TODO index other dataset files from repo
    # docs_url = relative_url # f"{BASE_URL}/{relative_url}?raw=1"
    # # docs_response = requests.get(docs_url)
    # # documents = docs_response.json()
    # df = pd.read_csv(docs_url)
    df = pd.DataFrame()
    data_path = data_path.rstrip('/') # prevent //
    qna_files = sorted(glob(data_path+'/qna-*.csv'))
    for file_name in qna_files:
        df_ = pd.read_csv(file_name) #, index_col=False)
        print(f' adding {file_name}: {df_.shape[0]} record(s)')
        df = pd.concat([df, df_]) #,ignore_index=True)

    documents = df.to_dict(orient="records")
    print(f" Fetched {len(documents)} document(s)")
    return documents


def load_index(data_path=DATA_PATH):
    documents = fetch_documents(data_path)

    index = minsearch.Index(
        text_fields=[
            "question",
            "text",
            "position",
            "section",
        ],
        keyword_fields=["id"],
    )

    index.fit(documents)
    return index


def setup_elasticsearch():
    print(f"Setting up Elasticsearch ({ELASTIC_URL})...")
    es_client = Elasticsearch(ELASTIC_URL)
    print(" Connected to Elasticsearch:", es_client.info())

    index_settings = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "question": {"type": "text"},
                "text": {"type": "text"},
                "interview": {"type": "keyword"},
                "section": {"type": "text"},
                "id": {"type": "keyword"},
                "question_text_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        },
    }

    try:
        es_client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
    except Exception as e:
        print('!! es_client.indices.delete:', e)
    es_client.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Elasticsearch index '{INDEX_NAME}' created")
    return es_client


def load_model():
    print(f"Loading model: {INDEX_MODEL_NAME}")
    return SentenceTransformer(INDEX_MODEL_NAME)


def index_documents(es_client, documents, model):
    print("Indexing documents...")
    for doc in documents:
        question = doc["question"]
        text = doc["text"]
        doc["question_text_vector"] = model.encode(question + " " + text).tolist()
        es_client.index(index=INDEX_NAME, document=doc)
    print(f" Indexed {len(documents)} documents")


def init_elasticsearch():
    # you may consider to comment <start>
    # if you just want to init the db or didn't want to re-index
    print("ElasticSearch: starting the indexing process...")

    documents = fetch_documents()
    model = load_model()
    es_client = setup_elasticsearch()
    index_documents(es_client, documents, model)
    # you may consider to comment <end>

    # print("Initializing database...")
    # init_db()

    print(" Indexing process completed successfully!")
    return es_client

SEARCH_RESULTS_NUM = 3 # 5

def elastic_search_text(query, position, index_name=INDEX_NAME):
    search_query = {
        "size": SEARCH_RESULTS_NUM,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields",
                    }
                },
                "filter": {"term": {"position": position}},
            }
        },
    }

    response = es_client.search(index=index_name, body=search_query)
    # variant with scores
    # return [(hit["_source"], hit["_score"]) for hit in response["hits"]["hits"]]
    return [hit["_source"] for hit in response["hits"]["hits"]]


def elastic_search_knn(field, vector, position, index_name=INDEX_NAME):
    knn = {
        "field": field,
        "query_vector": vector,
        "k": SEARCH_RESULTS_NUM,
        "num_candidates": 10000,
        "filter": {"term": {"position": position}},
    }

    search_query = {
        "knn": knn,
        "_source": ["text", "section", "question", "position", "id"],
    }

    response = es_client.search(index=index_name, body=search_query)

    return [hit["_source"] for hit in response["hits"]["hits"]]


if __name__ == "__main__":
    if USE_ELASTIC: 
        es_client = init_elasticsearch()

        # quick test
        position = 'de'
        query = 'What is Data Engineering?'
        print('\nTest query:', query)
        for search_type in ['Text', 'Vector']: 
            if search_type == 'Vector':
                index_model = load_model()
                vector = index_model.encode(query)
                search_results = elastic_search_knn('question_text_vector', vector, position)
            else:
                search_results = elastic_search_text(query, position)
            print(search_type, len(search_results), search_results)    
    else:
        print("MinSearch: Ingesting data...")
        index = load_index(data_path=DATA_PATH)
        print(f' Indexed {len(index.docs)} document(s)')

        # quick test
        position = 'de'
        query = 'What is Data Engineering?'
        print('\nTest query:', query)
        search_results = index.search(query, {'position': position}, num_results=3)
        print(len(search_results), search_results)    
