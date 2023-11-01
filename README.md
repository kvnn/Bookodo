## Local Setup
1. `git clone git@github.com:kvnn/Bookodo.git`
2. `cd Bookodo`
3. `cp app/.env.template app/.env` and (optionally) enter your open ai api key
4. `docker-compose build`
5. `docker-compose up` (you can safely ignore the initial `FileNotFound` Error - the celery.log will be created soon after)
6. visit http://localhost:8004
