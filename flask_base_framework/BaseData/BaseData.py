# -*- coding: utf-8 -*-

from Startup import db
from sqlalchemy import Column, Integer, String, DateTime, Text

class Base_Data(db.Model):

    __tablename__ = 'base_data'

    BASE_ID = Column(Integer, primary_key=True, autoincrement=True)

    Base_Text = Column(Text(), nullable=False)

    Base_Text2 = Column(String(20), nullable=True)

    Base_Num = Column(Integer , nullable=True)

    InertDate = Column(DateTime(), nullable=False)