from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
DATABASE_URL = "sqlite:///./reload_00.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Test model
class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# FastAPI setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    # Fetch all records from the database
    tests = db.query(Test).all()
    return templates.TemplateResponse("indicate_00.html", {"request": request, "tests": tests})

@app.post("/add/", response_class=HTMLResponse)
async def add_data(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    # Add new record to the database
    new_test = Test(name=name)
    db.add(new_test)
    db.commit()
    return await read_root(request, db)

@app.get("/api/data", response_class=JSONResponse)
async def get_data(db: Session = Depends(get_db)):
    tests = db.query(Test).all()
    return [{"id": test.id, "name": test.name} for test in tests]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)