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

At some moment of life we want a new job, right? So I decided to make my 2nd LLM project that helps Data and ML Engineers prepare for a job interview.
Why? Because just technical knowledge even validated by professional certification(s) is not enough to get a job. Usually interview questions have a bit different angle than certification exams. In addition, interviews include soft skills assessment and behavioral questions.

With right prompts ChatGPT can be a decent interview assistant. Still, it can hallucinate as not trained well for specific topics yet. Or you want to use your local Ollama (like me), but open models know even less?

That's where RAG comes in! RAG is Retrieval Augmented Generation - the process of optimizing the output of a large language model (LLM). It references your prepared knowledge base before generating a response. So instead of asking LLM about interview topics "from scratch", RAG based assistant first gets context from your knowledge base (like QnA records) and then provides you better focused answers. This is what I use in this project.

Just imagine, you can 'talk to your data', amazing!✨

## 🎯 Goals

This is my 2nd LLM project started during [LLM ZoomCamp](https://github.com/DataTalksClub/llm-zoomcamp)'24.

LLM Interview Assistant should assist users with their preparation to data/ML job interviews. It should provide a chatbot-like interface to easily find interview related information without looking through guides or websites.

As in the 1st project, I'm making it universal enough, so knowledge base can be extended to other professions, of course with some adjustments in RAG prompts.

Thanks to LLM ZoomCamp for the reason to keep learning new cool tools! 

## 🔢 Dataset

I collected questions with answers from sources like articles on respected Data professions related websites, and transformed them into a [dataset](/data). Now it includes 2 .csv files - with Data Engineering and Machine Learning topics. And I plan to load some more QnAs universal for Data related positions. I prepared app UI and backend extensible.

**Structure**: id, question, text (=answer), position, section.

Sections are used in search and help to focus on specific topics of the interview.

## :toolbox: Tech stack

* Frontend: 
    - UI: Streamlit web application for conversational interface
    - Monitoring: Grafana
* Backend:
    - Python 3.11/3.12
    - Docker and docker-compose for containerization
    - Elastic search to index interview questions-answers bank
    - OpenAI-compatible API, that supports working with Ollama locally, even without GPU
        * Ollama tested with Microsoft Phi 3/3.5 and Alibaba qwen2.5:3b models, they performed better than Google Flan-T5, Gemma 2
        * you can pull and test any model from [Ollama library](https://ollama.com/library)
        * with your own OPENAI_API_KEY you can choose gpt-3.5/gpt-4o
    - PostgreSQL to store asked questions, answers, evaluation (relevance) and user feedback

## 🚀 Instructions to reproduce

- [Setup environment](#hammer_and_wrench-setup-environment)
- [Start the app](#arrow_forward-start-the-app)
- [Interact with the app](#speech_balloon-interact-with-the-app)
- [Monitoring](#bar_chart-monitoring)
- [Retrieval evaluation](#retrieval-evaluation)
- [Best practices](#best-practices)

### :hammer_and_wrench: Setup environment

1. **Fork this repo on GitHub**. Or use `git clone https://github.com/dmytrovoytko/llm-interview-assistant.git` command to clone it locally, then `cd llm-interview-assistant`.
2. Create GitHub CodeSpace from the repo ‼️ **use 4-core - 16GB RAM machine type**.
3. **Start CodeSpace**
4. **Go to the app directory** `cd interview_assistant`
5. The app works in docker containers, **you don't need to install packages locally to test it**.
6. Only if you want to develop the project locally, you can run `pip install -r requirements.txt` (project tested on python 3.11/3.12).
6. **If you want to use gpt-3.5/gpt-4 API you need to correct OPENAI_API_KEY in `.env` file**, which contains all configuration settings. 
7. By default instructions (below) scripts will load Ollama/phi3.5 model. If you want to use also Ollama/phi3 or Ollama/qwen2.5:3b uncomment a line in `ollama_pull.sh`. Similarly you can load other Ollama models.

### :arrow_forward: Start the app

1. **Run `bash deploy.sh` to start all containers**, including elasticsearch, ollama, postgres, streamlit, grafana. It takes at least couple of minutes to download/build corresponding images, then get all services ready to serve. So you can make yourself some tea/coffee meanwhile. When the new log messages stop appering, press enter to return to a command line. 
![docker-compose up](/screenshots/docker-compose-00.png)

![docker-compose up](/screenshots/docker-compose-01.png)

2. Run `bash init_db_es.sh` 
* to create PostgreSQL tables:
* to ingest and index question database:

![init_db_es](/screenshots/init_db_es.png)


3. Run `bash ollama_pull.sh` to pull phi3/phi3.5 Ollama models

![Ollama pull](/screenshots/ollama_pulled.png)

If you want to use other models, you can modify this script accordingly, then update `app.py` to add your model names.

5. Finally, open streamlit app: switch to ports tab and click on link with port 8501 (🌐 icon).

![Ports streamlit open](/screenshots/streamlit-open.png)

### :speech_balloon: Interact with the app

1. Set query parameters - choose position, model, query parameters (search type - text, vector; response length - small, medium, long), enter your question.
2. Press 'Find the answer' button, wait for the response. For Ollama Phi3/qwen2.5 in CodeSpace response time was around a minute.
![streamlit Find the answer](/screenshots/streamlit-00.png)

3. RAG evaluation: check relevance evaluated by LLM (default model to use for this is defined in `.env` file).
![streamlit check](/screenshots/streamlit-02.png)

4. Give your feedback by pressing corresponding number of stars 🌟🌟🌟🌟🌟
- 1-2 are negative
- 4-5 are positive

Both types of evaluation are stored in the database and can be monitored.

5. App starts in wide mode by default. You can switch it off in streamlit settings (upper right corner).

### :bar_chart: Monitoring

You can monitor app performance in Grafana dashboard

1. Run `bash init_gr.sh` to create dashboard.
![Grafana init_gr](/screenshots/init_gr.png)

2. As with streamlit, switch to the PORTS tab and click on the link with port 3000 (🌐 icon). After loading Grafana use default credentials:
- Login: "admin"
- Password: "admin"


3. Click 'Dashboards' in the left pane and choose 'Interview preparation assistant'.

![Grafana dasboard](/screenshots/grafana-00.png)

4. Check out app performance

![Grafana dasboard](/screenshots/grafana-01.png)

### :stop_sign: Stop all containers

Run `docker compose down` in command line to stop all services.
Don't forget to remove downloaded images if you experimented with project locally! Use `docker images` to list all images and `docker image rm ...` to remove those you don't need anymore.

## Retrieval evaluation

Notebooks with text only and vector search retrieval evaluation are in [notebooks](/notebooks) directory.

I decided to experiment with different Ollama models to create ground thuth data for data Engineering QnA. To be honest, the results are poor enough IMHO. I think partially it is because of QnA knowledge base is not so specific as with exam dataset, as interview recommendations are quite vague. 
Anyway, with some models (like Llama3.2 it) I just didn't manage to get proper response in JSON parsable format. Surprisingly, Gemma 2 worked well enough with it. The results are in `ground-truth-data.csv` file. Questions are not very relevent to actually be a ground truth IMHO.

After all, the purpose is to learn, not to get a perfect result. So I tested min_search and Elastic search.

**MinSearch**:
- hit_rate 0.7722066133563864, MRR 0.661454506159499

**ElasticSearch**:
- text only: hit_rate 0.592, MRR 0.420

- vector_knn: hit_rate 0.705, MRR 0.581

- text_vector_knn: hit_rate 0.725, MRR 0.615

- question_text_vector_knn: hit_rate 0.744, MRR 0.633

- vector_combined_knn: hit_rate 0.747, MRR 0.635

I will continue experimenting with weights and boosting.

## Best practices
 * [x] Hybrid search: combining both text and vector search (Elastic search, encoding)
 * [x] User query rewriting 

## Next steps

I plan to:
- add more questions to the knowledge database, add other positions
- test more models (like Llama 3.2)
- fine tune prompts
- experiment with weights and boost to improve retrieval metrics

Stay tuned!

## Support

🙏 Thank you for your attention and time!

- If you experience any issue while following this instruction (or something left unclear), please add it to [Issues](/issues), I'll be glad to help/fix. And your feedback, questions & suggestions are welcome as well!
- Feel free to fork and submit pull requests.

If you find this project helpful, please ⭐️star⭐️ my repo 
https://github.com/dmytrovoytko/llm-interview-assistant to help other people discover it 🙏

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko
