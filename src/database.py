# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Annotated
from fastapi import Depends
from src.global_variables import DB_URI, REDIS_HOST, REDIS_PORT
from sqlalchemy import Column, DateTime, func
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI, Request


# postgres database url
postgres_url = DB_URI

# create engine for database connection
engine = create_async_engine(postgres_url)

# creating session for orms
session = sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession)


# base class initiated
class Base(DeclarativeBase):
    __abstract__ = True

    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default = func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)


# redis setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
        setting up redis server on will start on startup
    '''

    print("Starting redis server on startup...")
    app.state.redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # checking if redis server started
    try:
        if await app.state.redis_client.ping():
            print("Redis connected successfully...")
    except Exception as err:
        print("[ERROR] Redis is not connected...", err)

    yield

    print("Shutting down redis server on shutdown...")
    await app.state.redis_client.close()




async def get_session():
    '''
        function to provide session of orm of api endpoints
    '''
    async with session() as db:
        yield db



def get_redis_client(request: Request):
    '''
        return redis client
    '''
    return request.app.state.redis_client



# Session is annotated to be used in apis later directly
session_dep = Annotated[AsyncSession, Depends(get_session)]
