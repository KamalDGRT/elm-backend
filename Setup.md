# Local Setup

- Setup Python Virtual Environment `virtualenv`
- In the Project Root Directory, run this command `py -m venv env`
- Activate that virtual environemnt.
- Install the dependencies - `pip install -r requirements.txt`
- Start the Xampp Server (Apache and MySQL)
- Create an empty database `database_name`
- Setup the `.env` with appropriate values. Sample config is below.

```r
DATABASE_HOSTNAME=localhost
DATABASE_PORT=3306
DATABASE_USERNAME= database_username
DATABASE_PASSWORD= database_password
DATABASE_NAME=database_name
SECRET_KEY=randomTextWithAlpaNumericChars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEPLOYMENT_ENV=dev
```

- now run `alembic upgrade head` in the CLI. This will create the tables.

- Start the API server : `uvicorn app.main:app --reload`

- In one of the browser tab, open this url: http://127.0.0.1:8000/docs`
