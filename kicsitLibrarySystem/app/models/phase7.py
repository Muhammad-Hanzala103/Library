from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ImportBatch(Base):
    __tablename__ = "importbatches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    import_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Previewed", index=True, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    errors: Mapped[list["ImportErrorRow"]] = relationship("ImportErrorRow", back_populates="batch")


class ImportErrorRow(Base):
    __tablename__ = "importerrors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("importbatches.id", ondelete="CASCADE"), index=True, nullable=False)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    row_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)

    batch: Mapped[ImportBatch] = relationship("ImportBatch", back_populates="errors")

