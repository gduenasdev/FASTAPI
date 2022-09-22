from email import message
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
        password='Duenas', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id":1},
{"title": "favorite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post

def find_index_post(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return  i

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM post") SQL implementation
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO post (title, content, published) 
    #     VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit() SQL implementation
    new_post =models.Post(**post.dict()) # automatically unpacks dict
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM post WHERE id=%s""", (str(id),))
    # post = cursor.fetchone() SQL implementation
    post = db.query(models.Post).filter(models.Post.id == id).first() # equivalent to a WHERE
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found")
    return {'post_detail': post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM post WHERE id=%s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit() SQL implementation
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id: {id} does not exist")
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE post SET title=%s, content=%s, published=%s WHERE id=%sRETURNING *""",
    # (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit() SQL implementation
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id: {id} does not exist")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}