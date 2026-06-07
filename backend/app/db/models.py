from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="employee")
    department: Mapped[str] = mapped_column(String, default="General")
    password_hash: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String, index=True)
    chunks_created: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="indexed")
    source_path: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(String, default="General")
    document_type: Mapped[str] = mapped_column(String, default="Policy")
    access_level: Mapped[str] = mapped_column(String, default="internal")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))
    chunk_id: Mapped[str] = mapped_column(String, index=True)
    text: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(nullable=True)

    document: Mapped[Document] = relationship(back_populates="chunks")


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    question: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String, default="qa")
    answer: Mapped[str] = mapped_column(Text)
    validation_status: Mapped[str] = mapped_column(String, default="not_evaluated")
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    average_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    faithfulness: Mapped[float] = mapped_column(Float, default=0.0)
    context_precision: Mapped[float] = mapped_column(Float, default=0.0)
    answer_relevancy: Mapped[float] = mapped_column(Float, default=0.0)
    context_recall: Mapped[float] = mapped_column(Float, default=0.0)
    hallucination_rate: Mapped[float] = mapped_column(Float, default=0.0)

    cases: Mapped[list["EvaluationCase"]] = relationship(back_populates="run")


class EvaluationCase(Base):
    __tablename__ = "evaluation_cases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    run_id: Mapped[str] = mapped_column(ForeignKey("evaluation_runs.id"))
    case_id: Mapped[str] = mapped_column(String, index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    expected_source: Mapped[str] = mapped_column(String, default="")
    top_source: Mapped[str | None] = mapped_column(String, nullable=True)
    faithfulness: Mapped[float] = mapped_column(Float, default=0.0)
    context_precision: Mapped[float] = mapped_column(Float, default=0.0)
    answer_relevancy: Mapped[float] = mapped_column(Float, default=0.0)
    context_recall: Mapped[float] = mapped_column(Float, default=0.0)
    passed: Mapped[bool] = mapped_column(Integer, default=0)  # SQLite compat bool

    run: Mapped[EvaluationRun] = relationship(back_populates="cases")
