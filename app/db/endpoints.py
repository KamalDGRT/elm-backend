from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, Integer, Boolean, Text, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class Endpoint(Base):
    __tablename__ = "endpoint"

    endpoint_id = Column(Integer, primary_key=True, index=True)
    endpoint_name = Column(String(length=256), nullable=False, unique=True)
    is_common = Column(Boolean, nullable=False)
    is_disabled = Column(Boolean, nullable=False)
    method = Column(String(length=10), nullable=False)
    category = Column(Text(), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    created_by = Column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_by = Column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])


class EndpointRole(Base):
    __tablename__ = "endpoint_role"
    endpoint_role_id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(
        Integer, ForeignKey("endpoint.endpoint_id", ondelete="CASCADE"), nullable=False
    )
    role_id = Column(
        Integer, ForeignKey("role.role_id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    endpoint = relationship("Endpoint", foreign_keys=[endpoint_id])
    role = relationship("Role", foreign_keys=[role_id])
