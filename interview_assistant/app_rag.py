import os
import time
import json

from openai import OpenAI

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
INDEX_MODEL_NAME = os.getenv("INDEX_MODEL_NAME", "multi-qa-MiniLM-L6-cos-v1")
INDEX_NAME = os.getenv("INDEX_NAME")
SEARCH_RESULTS_NUM = 3 # 5

es_client = Elasticsearch(ELASTIC_URL)
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
MODEL_NAME = os.getenv("MODEL_NAME") # "ollama/phi3.5" # openai/gpt-4o-mini


index_model = SentenceTransformer(INDEX_MODEL_NAME)

DEBUG = True

def print_log(message):
    print(message, flush=True)


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
    return [hit["_source"] for hit in response["hits"]["hits"]]


def elastic_search_knn(field, vector, position, index_name="interview-questions"):
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

    es_results = es_client.search(index=index_name, body=search_query)

    return [hit["_source"] for hit in es_results["hits"]["hits"]]

def response_length_prompt(max_length):
    if max_length<=200:
        return f"Responses should be brief and concise with minimal narration. One paragraph, no more than three sentences, no more than {max_length} words." 
    elif max_length<=500:
        return f"Responses should be with minimal narration. Two paragraphs, no more than three sentences each, no more than {max_length} words." 
    else: #if max_length<=1000:
        return f"Responses should be thorough and well structured, no more than {max_length} words." 

def build_prompt(query, position_choice, search_results, max_length):
    # TODO max_length
    response_limits = response_length_prompt(max_length)
    prompt_template = """
You're an experienced career coach who worked as a technical recruiter and helps {position_choice}s prepare for job interviews. Answer the QUESTION based on the CONTEXT from our knowledge database.
Use only the facts from the CONTEXT when answering the QUESTION.
{response_limits}

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = "\n\n".join(
        [
            f"\nsection: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}"
            for doc in search_results
        ]
    )

    prompt = prompt_template.format(question=query, position_choice=position_choice, context=context, response_limits=response_limits).strip()
    if DEBUG:
        print_log(f'Search_results: {len(search_results)}')
        print_log(f'Prompt: {max_length} {prompt}')
        # print_log(f'Context: {context}')
    return prompt


def llm(prompt, model_choice, max_length=100):
    # TODO max_length in tokens?
    start_time = time.time()
    if model_choice.startswith('ollama/'):
        response = ollama_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    # TODO add microsoft/phi via HF
    elif model_choice.startswith('openai/'):
        response = openai_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")
    
    response_time = time.time() - start_time
    
    return answer, tokens, response_time


def evaluate_relevance(question, answer):
    evaluation_prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer to the given question.
    Based on the relevance of the generated answer, you will classify it
    as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()

    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, MODEL_NAME) # 'openai/gpt-4o-mini'

    if DEBUG:
        print_log(f'Evaluation: {evaluation}')
    
    if evaluation.startswith('```json'):
        # remove extra formatting ```json ... ```
        evaluation = evaluation[7:-3].strip()
        # print('evaluate_relevance', evaluation)

    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        print('!! evaluation parsing failed:', evaluation)
        if evaluation.find("RELEVANT")>=0:
            return "RELEVANT", evaluation, tokens
        elif evaluation.find("PARTLY_RELEVANT")>=0:
            return "PARTLY_RELEVANT", evaluation, tokens
        elif evaluation.find("NON_RELEVANT")>=0:
            return "NON_RELEVANT", evaluation, tokens
        else:
            return "UNKNOWN", f"Failed to parse evaluation. {evaluation}", tokens
    except:
        print('!! evaluation parsing failed:', evaluation)
        if evaluation.find("RELEVANT")>=0:
            return "RELEVANT", evaluation, tokens
        elif evaluation.find("PARTLY_RELEVANT")>=0:
            return "PARTLY_RELEVANT", evaluation, tokens
        elif evaluation.find("NON_RELEVANT")>=0:
            return "NON_RELEVANT", evaluation, tokens
        else:
            return "UNKNOWN", f"Failed to parse evaluation. {evaluation}", tokens


def calculate_openai_cost(model, tokens):
    openai_cost = 0
    # TODO update costs
    if model == 'openai/gpt-3.5-turbo':
        openai_cost = (tokens['prompt_tokens'] * 0.0015 + tokens['completion_tokens'] * 0.002) / 1000
    elif model in ['openai/gpt-4o', 'openai/gpt-4o-mini']:
        openai_cost = (tokens['prompt_tokens'] * 0.03 + tokens['completion_tokens'] * 0.06) / 1000

    return openai_cost


def get_answer(query, position_choice, model_choice, search_type, response_length):
    positions = {"data engineer": "de", "machine learning engineer": "mle"}
    position = positions.get(position_choice, "de")

    if search_type == 'Vector':
        vector = index_model.encode(query)
        search_results = elastic_search_knn('question_text_vector', vector, position)
    else:
        search_results = elastic_search_text(query, position)

    if response_length == 'S':
        max_length = 200
    elif response_length == 'M':
        max_length = 500
    else: # 'L'
        max_length = 1000

    prompt = build_prompt(query, position_choice, search_results, max_length)

    answer, tokens, response_time = llm(prompt, model_choice, max_length)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

    openai_cost = calculate_openai_cost(model_choice, tokens)
 
    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': openai_cost
    }
