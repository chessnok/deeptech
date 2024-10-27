# EasyDocs by DeepTech<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="50"/></h1>
We present EasyDocs service, which will help users to facilitate their work with documentation and technical information by asking our AI model for an answer. 
Any user will be able to contact the model via a Telegram bot or on our website and ask a question. 
Our service provides a number of features that make it a unique solution to this problem:
1. Working with context. The model remembers the context of communication with the user and also processes it when issuing an answer. At any time the user can create a new context. 
2. Dealing with incorrect questions. Our model is able to recognize questions that are not related to documentation. Also, if a question was asked about the service, the answer to which is not in the documentation, the chatbot will offer to contact the administrator who will be able to advise the user. 
3. scalability. Our service has a microservice architecture, so the model can be easily used in other tasks. We have developed an authentication system through Apikey that will allow us to give access to the model to third party users. For this purpose, we also developed full Swagger documentation for working with the model. 


The stack of our solution: 
Flask, Telebot, ML libraries

### Installation

1. Run `docker-compose up -d`
2. Run `docker-compose exec tg_bot python init.py`
3. Run `docker-compose exec backend python init.py`
4. Open [TgBot](https://t.me/EasyDocsDeepTech_bot) or [Website](localhost)
5. Enjoy!


## Technologies

#### Backend

- Flask
- TelegramBotApi
- Docker
- Docker-compose
- PostgreSQL
- Swagger

#### Frontend

- JavaScript
- HTML
- CSS

![Структура проекта](/assets/image2.jpg "Структура проекта")
Структура проекта
![Пользовательские сценарии при обращении к боту](/assets/image1.jpg "Пользовательские сценарии")
Пользовательские сценарии telegram бота
