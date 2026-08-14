from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(length=128), index=True, nullable=False)
    show_on_menu = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(length=300), nullable=False)
    email = Column(String(length=200), nullable=False, unique=True)
    user_name = Column(String(length=100), nullable=True, unique=True)
    password = Column(String(length=100), nullable=False)
    login_allowed = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    refresh_token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    refresh_token = Column(Text(), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user = relationship("User", foreign_keys=[user_id])


class UserRole(Base):
    __tablename__ = "user_role"
    user_role_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    role_id = Column(
        Integer, ForeignKey("role.role_id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role", foreign_keys=[role_id])


class UpdatePasswordLog(Base):
    __tablename__ = "update_password_log"
    log_id = Column(Integer, primary_key=True, index=True)
    # user_id of the record for which the password is updated/changed
    user_id = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_by = Column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", foreign_keys=[user_id])
    updater = relationship("User", foreign_keys=[updated_by])
