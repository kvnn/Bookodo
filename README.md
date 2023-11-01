## Demo
This project can be demoed from a cloud deployment (an ec2 public IP should be provided), or via a local setup (see below)

## Local Setup
1. `git clone git@github.com:kvnn/Bookodo.git`
2. `cd Bookodo`
3. `cp app/.env.template app/.env` and (optionally) enter your open ai api key
4. `docker-compose build`
5. `docker-compose up`
6. from another terminal:
   1. `docker-compose run web alembic revision --autogenerate -m "init migration"`
   2. `docker-compose run web alembic upgrade head `
7. visit http://localhost:8004
8.  I'd like to remove the redundancy of POSTGRES_USER, POSTGRES_DB, and DB_CONNECTION in .env / config.py


## Cloud Setup
1. the `main.tf` terraform config is designed for AWS.
2. in `variables.tf`, modify the value for `server_ssh_key_local_path` to an ssh key that corresponds to an AWS key
3. in `variables.tf`, modify `s3_bucket_name_media` to a bucket that you own
4. optionally, in the root directory, create a file called `terraform.tfvars` with `openai_api_key = "{your openai key}"`
5. `terraform apply`