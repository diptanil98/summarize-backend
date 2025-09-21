from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

# Import routers directly (assuming summarizer.py and auth.py are in the same folder as main.py)
from summarizer import router as summarizer_router
from auth import router as auth_router

# Create FastAPI app instance
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is running"}

# Health check route
@app.head("/")
def health_check():
    return

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins in Railway; adjust for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers after app initialization
app.include_router(summarizer_router)
app.include_router(auth_router, prefix="/api")

# OpenAPI customization (if needed)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="LegalizeAI",
        version="1.0.0",
        description="API with JWT auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if _name_ == "_main_":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)