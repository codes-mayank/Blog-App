from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.models import Blog, User
from app.database import get_db
from app.schemas import BlogBase, BlogCreate, BlogOut, BlogOutWithAuthor, BlogUpdate, Token
from app.core.security import get_current_user
from app.utils.blog import create_slug


router = APIRouter()

@router.get('/', response_model=List[BlogOutWithAuthor])
def read_all_blogs(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    """Read all blog posts with author details"""
    
    blogs = (
        db.query(
            Blog.id,
            Blog.slug,
            Blog.title,
            Blog.body,
            Blog.author_id,
            User.full_name.label("author_fullname"),
            User.username.label("author_username"),
        )
        .join(User, Blog.author_id == User.id)
        .filter(Blog.is_deleted == False)
        .order_by(Blog.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return blogs

@router.post('/', response_model=BlogOut)
def create_blogs(blog: BlogCreate, db: Session = Depends(get_db), token: Token = Depends(get_current_user)):
    """Create a new blog post"""
    new_blog = Blog(
        body=blog.body,
        title=blog.title,
        author_id=token.user_id,
        slug=create_slug(blog.title)
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@router.get('/{slug}', response_model=BlogOutWithAuthor)
def read_blog(slug: str, db: Session = Depends(get_db)):
    """Read a single blog post by slug with author details"""
    blog = (
        db.query(
            Blog.id,
            Blog.slug,
            Blog.title,
            Blog.body,
            Blog.author_id,
            User.full_name.label("author_fullname"),
            User.username.label("author_username"),
        )
        .join(User, Blog.author_id == User.id)
        .filter(Blog.slug == slug, Blog.is_deleted == False)
        .first()
    )
    if blog is None:
        return {'error': 'This blog post does not exist'}
    return blog


@router.delete('/{id}', response_model=dict)
def delete_blog(id: int, db: Session = Depends(get_db), token: Token = Depends(get_current_user)):
    """Delete a blog post by ID"""

    blog = db.query(Blog).filter(Blog.id == id, Blog.is_deleted == False).first()

    if blog is None:
        raise HTTPException(status_code=400, detail="Blog post not found")
    if blog.author_id != token.user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this blog post")
    
    delete_stmt = update(Blog).where(Blog.id == id).values(is_deleted=True)
    db.execute(delete_stmt)
    db.commit()
    db.refresh(blog)

    return {'message': 'This blog post has been deleted'}


@router.put('/{id}', response_model=BlogBase)
def update_blog(blog: BlogUpdate, id: int, db: Session = Depends(get_db), token: Token = Depends(get_current_user)):
    """Update a blog post by ID"""

    blog_db = db.query(Blog).filter(Blog.id == id, Blog.is_deleted == False).first()

    if blog_db is None:
        raise HTTPException(status_code=400, detail="Blog post not found")
    if blog_db.author_id != token.user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this blog post")
    
    update_stmt = update(Blog).where(Blog.id == id).values(title=blog.title, body=blog.body)
    db.execute(update_stmt)
    db.commit()
    db.refresh(blog_db)

    return blog_db

