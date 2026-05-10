from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime\
from sqlalchemy.ext.declarative import declarative_base\
from sqlalchemy.orm import sessionmaker\
\
engine = create_engine('sqlite:///database.db')\
Base = declarative_base()\
\
class MarketData(Base):\
\\t__tablename__ = 'market_data'\
\\tid = Column(Integer, primary_key=True)\
\\ttimestamp = Column(DateTime)\
\\topen = Column(Float)\
\\thigh = Column(Float)\
\\tlow = Column(Float)\
\\tclose = Column(Float)\
\\tvolume = Column(Float)\
\
class Trades(Base):\
\\t__tablename__ = 'trades'\
\\tid = Column(Integer, primary_key=True)\
\\ttimestamp = Column(DateTime)\
\\tsymbol = Column(String)\
\\tside = Column(String)\
\\tamount = Column(Float)\
\\tprice = Column(Float)\
\
class AIAudit(Base):\
\\t__tablename__ = 'ai_audit'\
\\tid = Column(Integer, primary_key=True)\
\\ttimestamp = Column(DateTime)\
\\tdecision = Column(String)\
\\tconfidence = Column(Float)\
\
Base.metadata.create_all(engine)