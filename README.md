## Local Setup
1. `git clone git@github.com:kvnn/Bookodo.git`
2. `cd Bookodo`
3. `cp app/.env.template app/.env` and (optionally) enter your open ai api key
4. `docker-compose build`
5. `docker-compose up` (you can safely ignore the initial `FileNotFound` Error - the celery.log will be created soon after)
6. visit http://localhost:8004

## Technologies Used
1. FastAPI: A modern, fast web framework for building APIs with Python. FastAPI is designed to be easy to use while ensuring high performance. It leverages standard Python type hints to validate data, serialize, and deserialize data, and automatically generate OpenAPI documentation. In a CRUD web app, FastAPI would handle HTTP requests and serve as the backend, processing create, read, update, and delete operations.

2. SQLAlchemy: This is a Python SQL toolkit and Object-Relational Mapping (ORM) library. It makes switching between datbase engines trivial (in this case, just switching modifying a few fields in `.env`) . It provides a full suite of well-known enterprise-level persistence patterns and is designed for efficient and high-performing database access. SQLAlchemy would be used in the web app to interact with the database, abstracting SQL commands through Python objects for all the CRUD operations.

3. Bootstrap 5: This is the latest major version of the Bootstrap framework, a powerful front-end toolkit for developing responsive, mobile-first websites. Bootstrap 5 provides pre-styled components and layout utilities to help you design your web application's user interface quickly. In a CRUD web app, Bootstrap would provide the styling and components for forms, tables, and other UI elements.

4. Alpine.js: A minimal JavaScript framework for composing behavior directly in your markup. Alpine.js is often used as a lighter alternative to Vue or React for adding interactivity to web pages. It's designed to be simple and straightforward, with a declarative syntax that's easy to read and write. In a CRUD app, Alpine.js can be used to create a dynamic UI, handling things like form submissions, data updates without a page refresh, and other interactive elements.

5. jQuery: A fast, small, and feature-rich JavaScript library. It makes things like HTML document traversal and manipulation, event handling, and animation much simpler with an easy-to-use API that works across a multitude of browsers. 

## Project Setup
Docker was chosen so that the demo app can be built and ran on any machine. Upon the initial `up`, the `main.py` file will create tables from `models.py` and seed the default sqlite database with the `books.json` values. Otherwise, `main.app` is meant to be a simple routing file, with most business logic in the `services` files. `crud.py` is meant to abstract most of the fetching from the database, but there are some exceptions in `services` and `models.py` that interface with the database directly (my approach here is to keep the app as simple and straight forward as possible, as opposed to following patterns perfectly). The optional A.I. generation is isolated to `services/list_image.py` which spins out a Celery worker (defined in `worker.py`) to generate a "List Image". 