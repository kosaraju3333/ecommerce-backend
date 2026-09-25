from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.database import engine, Base

from app.models.product import Product
from app.models.user import User
from app.models.cart import Cart, CartItem

from app.routers.products import router as product_router
from app.routers.auth import router as auth_router
from app.routers.cart import router as cart_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="E-Commerce Backend API",
    description="Production-style eCommerce REST API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product_router)
app.include_router(auth_router)
app.include_router(cart_router)


@app.get("/")
def root():
    return {
        "message": "E-Commerce Backend API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "UP"
    }