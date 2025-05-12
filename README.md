# Chatbot für das Deutsche Recht

This project introduces Chatbot für das Deutsche Recht, a tool designed to act as a "first responder" for addressing legal issues within the German legal domain, specifically aimed at aiding laypersons, including foreigners. Utilizing state of the art Large Language Models, the Chatbot allows direct interaction with legal information, bypassing intermediate steps, like online forums and or lawyers. It provides clear, accessible legal guidance in both German and English tailored to user queries and legal contexts. 

## Setup
### Backend
Start by cloning the repo.

Then you will need to create an environment for the backend.

```
cd law_qa
cd backend
conda env create -f environment.yml
conda activate law_qa_env
```

After activating the environment and installing the related libraries you will also need a Vector Database instance. We chose Qdrant. For this command to work you will need docker which you can install from https://docs.docker.com/manuals/ and then you should follow the steps for Installation. To create it locally:

```
cd law_qa
docker-compose up
```

After creating the Vector Database. You need to crawl and scrape the data from the web, since Vector DB and the Referenced Lookup depends on it. The git repository already includes the scraped data. If you still want to do a fresh start, (It takes a long time):

```
cd backend
python main_download_law_books.py
```

After that the data should be put in the Vector Databas. This process takes around 90 minutes:


```
python main_index_vector_db.py
```

After everything is done you can try to run the backend by:

```
python main_start_api_server.py
```
You can check the docs at: http://0.0.0.0:5000/docs


### Frontend

In the Frontend directory, you can run:

```
npm install
```

install dependencies for React

```
npm start
```
You can check the app at http://localhost:3000/ 

You can also inspect the Qdrant Vector DB with http://localhost:6333/dashboard#/collections
