from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JwtRole(Base):
    __tablename__ = 'jwt_role'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(64), unique=True)
    bound_claims = Column(Text)
    nomad_claims = Column(Text)


class JwtConfig(Base):
    __tablename__ = 'jwt_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    jwks_url = Column(Text)
    bound_issuer = Column(Text)
