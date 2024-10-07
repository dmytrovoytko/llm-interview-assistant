# LLM project Interview Preparation Assistant

Pet project / 2nd Capstone project for DataTalks.Club LLM ZoomCamp`24: 

RAG application based on interview preparation questions for Data Engineers, Machine Learning Engineers.

![LLM project Interview Preparation Assistant](/screenshots/llm-interview-assistant.png)

Project can be tested and deployed in cloud virtual machine (AWS, Azure, GCP), **GitHub CodeSpaces** (the easiest option, and free), or even locally with/without GPU! Works with Ollama and ChatGPT.

For GitHub CodeSpace option you don't need to use anything extra at all - just your favorite web browser + GitHub account is totally enough.

## :toolbox: Tech stack

* Frontend: 
    - UI: Streamlit web application for conversational interface
    - Monitoring: Grafana
* Backend:
    - Python 3.11/3.12
    - Docker and docker-compose for containerization
    - Elastic search to index interview questions-answers bank
    - OpenAI-compatible API, that supports working with Ollama locally, even without GPU
        * Ollama tested with Microsoft Phi 3/3.5 model, performs better than Gemma
        * You can pull and test any model from [Ollama library](https://ollama.com/library)
        * with your own OPENAI_API_KEY you can choose gpt-3.5/gpt-4o
    - PostgreSQL to store asked questions, answers, evaluation (relevance) and user feedback
