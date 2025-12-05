from fastapi import FastAPI

# from app.models import Base
# from app.database import engine

from app.api.auth import router as auth_router
from app.api.blog import router as blog_router


app = FastAPI(title='blog app')

# Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix='/auth', tags=['Auth'])
app.include_router(blog_router, prefix='/posts', tags=['Blogs'])

@app.get('/')
def root():
    return {'message': 'Welcome to the blog site'}

