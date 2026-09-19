# Overview

This project uses python to connect to firestore, and this is to practice how to make a connection with this service in an very esay way, creating a todo list that let create lists or projects where we can add tasks for every list and perform CRUD operations

[Software Demo Video](https://youtu.be/tfavYWypB4k)

# Cloud Database

I am using Firestore, using just two tables of projects and tasks, every task keeps the id of the project object, as a foreing key, so we we ask for watching the tasks of a single project we can get all tasks related to it.

# Development Environment

We are using python because it's sintax its very easy to write and let me create a terminal interface where we can perform the several taks we need. It was just required to install firebase_admin that return a client that handle all operations to firebase. In the root of the project there is a JSON key file that keeps all string connection to database, for testing porpuses in other devices, you just need to initialize a firebase project in their page, get a JSON file, a raname it whatever you want and the Variable that will store tha same name of the file, it is SERVICE_ACCOUNT_FILE variable.

# Useful Websites

- [FIRESTORE CON PYTHON | PYTHON TUTORIAL](https://www.youtube.com/watch?v=u1KZUIvI_Uo)
- [FIRESTORE CON PYTHON | PYTHON TUTORIAL | PARTE 2 FINAL ](https://www.youtube.com/watch?v=rGgl9Ze8nAE&t=601s)
- [Firestore official page](https://firebase.google.com/docs/firestore/quickstart-server?hl=es-419#python)

# Future Work

- Http endpoints for connecting with a frontend
- Middleware, authorization, authentication, error handling, data validation
- Make it a backend server with django