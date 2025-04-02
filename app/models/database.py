from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# สร้าง SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./chujai.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# สร้าง SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# สร้าง Base class
Base = declarative_base()

# Dependency สำหรับ database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    content = Column(Text)
    embedding_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship กับ tags
    tags = relationship("NoteTag", back_populates="note")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    
    # Relationship กับ notes
    notes = relationship("NoteTag", back_populates="tag")

class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    # Relationships
    note = relationship("Note", back_populates="tags")
    tag = relationship("Tag", back_populates="notes")

# สร้าง tables ทั้งหมดใน database
Base.metadata.create_all(bind=engine)
