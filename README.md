# LLM project Interview Preparation Assistant

Pet project / 2nd Capstone project for DataTalks.Club LLM ZoomCamp`24: 

RAG application based on interview preparation questions for Data Engineers, Machine Learning Engineers.

![LLM project Interview Preparation Assistant](/screenshots/llm-interview-assistant.png)

Project can be tested and deployed in cloud virtual machine (AWS, Azure, GCP), **GitHub CodeSpaces** (the easiest option, and free), or even locally with/without GPU! Works with Ollama and ChatGPT.

For GitHub CodeSpace option you don't need to use anything extra at all - just your favorite web browser + GitHub account is totally enough.

## Problem statement

- [x] I made an Exam Preparation Assistant as the 1st LLM RAG app project
- [x] Then I successfully passed my Google Cloud Professional Data Engineer [exam](https://github.com/dmytrovoytko/DmytroVoytko/blob/master/achievements/GCP-PDE-cert.png)
- [ ] What's the next step? Right - Interview Preparation!

At some moment of life we want a new job, right? So I decided to make my 2nd LLM project that helps Data and ML Engineers prepare for a job Interview.
Why? Because just technical knowledge even validated by professional certification(s) is not enough to get a job. Usually interview questions have a bit different angle than certification exams. In addition, interviews include soft skills assessment and behavioral questions.

With right prompts ChatGPT can be a decent interview assistant. Still, it can hallucinate as not trained well for specific topics yet. Or you want to use your local Ollama (like me), but open models know even less?

That's where RAG comes in! RAG is Retrieval Augmented Generation - the process of optimizing the output of a large language model (LLM). It references your prepared knowledge base before generating a response. So instead of asking LLM about exam topics "from scratch", RAG based assistant first gets context from your knowledge base (like QnA records) and then provides you better focused answers. This is what I use in this project.

Just imagine, you can 'talk to your data'!

## 🎯 Goals

This is my 2nd LLM project started during [LLM ZoomCamp](https://github.com/DataTalksClub/llm-zoomcamp)'24.

LLM Interview Assistant should assist users with their preparation to data/ML job interviews. It should provide a chatbot-like interface to easily find interview related information without looking through guides or websites.

As in the 1st project, I'm making it universal enough, so knowledge base can be extended to other professions, of course with some adjustments in RAG prompts.

Thanks to LLM ZoomCamp for the reason to keep learning new cool tools! 

## Dataset

I decided to collect questions with answers from sources like articles on respected Data professions related websites, and transform them into a [dataset](/data). Now it includes 2 .csv files - with Data Engineering and Machine Learning topics. And I plan to load some more QnAs universal for Data related positions. I prepared app UI and backend extensible.

**Structure**: id, question, text (=answer), position, section.

Sections used in search and help to focus on specific topics of the interview.

## :toolbox: Tech stack

* Frontend: 
    - UI: Streamlit web application for conversational interface
    - Monitoring: Grafana
* Backend:
    - Python 3.11/3.12
    - Docker and docker-compose for containerization
    - Elastic search to index interview questions-answers bank
    - OpenAI-compatible API, that supports working with Ollama locally, even without GPU
        * Ollama tested with Microsoft Phi 3/3.5 model, performs better than Flan-T5, Gemma
        * You can pull and test any model from [Ollama library](https://ollama.com/library)
        * with your own OPENAI_API_KEY you can choose gpt-3.5/gpt-4o
    - PostgreSQL to store asked questions, answers, evaluation (relevance) and user feedback
