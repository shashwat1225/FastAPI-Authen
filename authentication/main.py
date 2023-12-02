from fastapi import FastAPI
import uvicorn
from sql_app.database import get_db
from authentication import auth
from authentication import error_responses
app = FastAPI()


def main():
    db, _ = get_db()
    auth.auth_api(app, db)
    error_responses.handlers(app)
    uvicorn.run(app)


if __name__ == "__main__":
    main()