from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, tables, customers, waiters, chefs, auth
from db import init_db

app = FastAPI(title="RMOS Sprint1 API", version="0.1.0")

# If you plan to host API and SPA under same origin via Nginx, CORS isn't strictly needed.
# Keep it permissive for local testing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

#app.include_router(health.router, prefix="/api")
#app.include_router(auth.router, prefix="/api")
#app.include_router(tables.router, prefix="/api")
#app.include_router(customers.router, prefix="/api")
#app.include_router(waiters.router, prefix="/api")
#app.include_router(chefs.router, prefix="/api")


# Cambia esto en todos tus routers en main.py
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tables.router)
app.include_router(customers.router) # Sin el prefix="/api"
app.include_router(waiters.router)
app.include_router(chefs.router)