from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.database import get_db, Note, Tag, NoteTag
from app.services.rag_service import rag_service

router = APIRouter()

class TagCreate(BaseModel):
    name: str

class NoteBase(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    embedding_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/notes/", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """สร้าง note ใหม่พร้อม embeddings"""
    # สร้าง note ในฐานข้อมูล
    db_note = Note(
        title=note.title,
        content=note.content
    )
    db.add(db_note)
    db.flush()  # เพื่อให้ได้ note.id

    # สร้าง embeddings
    metadata = {
        "note_id": db_note.id,
        "title": note.title
    }
    embedding_id = await rag_service.add_to_vectorstore(note.content, metadata)
    db_note.embedding_id = embedding_id

    # จัดการ tags
    for tag_name in note.tags:
        # ค้นหาหรือสร้าง tag
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()
        
        # เชื่อม note กับ tag
        note_tag = NoteTag(note_id=db_note.id, tag_id=tag.id)
        db.add(note_tag)

    db.commit()
    return db_note

@router.get("/notes/", response_model=List[NoteResponse])
def list_notes(
    skip: int = 0,
    limit: int = 10,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """ดึงรายการ notes ทั้งหมด"""
    query = db.query(Note)
    
    if tag:
        query = query.join(NoteTag).join(Tag).filter(Tag.name == tag)
    
    notes = query.offset(skip).limit(limit).all()
    return notes

@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """ดึงข้อมูล note ตาม ID"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/notes/search/")
async def search_notes(query: str, k: int = 3):
    """ค้นหา notes ที่คล้ายกับ query"""
    results = await rag_service.search_similar(query, k)
    return results

@router.post("/notes/ask/")
async def ask_question(
    question: str,
    chat_history: List = []
):
    """ถามคำถามโดยใช้ข้อมูลจาก notes"""
    response = await rag_service.ask_question(question, chat_history)
    return response

@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """ลบ note พร้อม embeddings"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # ลบ embeddings
    if note.embedding_id:
        await rag_service.delete_embeddings(note.embedding_id)
    
    # ลบ note
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}
