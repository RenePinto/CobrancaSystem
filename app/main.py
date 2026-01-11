from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, history, invoices, reports, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CobrancaSystem API", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(invoices.router)
app.include_router(reports.router)
app.include_router(history.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
