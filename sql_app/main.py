from fastapi import FastAPI
import uvicorn
from sql_app.database import get_db, Base
import sql_app.models
app = FastAPI()


def main():
    db, engine = get_db()
    Base.metadata.create_all(bind=engine)
    # Base.metadata.drop_all(bind=engine)

    db.commit()
    uvicorn.run(app)


if __name__ == "__main__":
    main()