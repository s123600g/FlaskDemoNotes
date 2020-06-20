# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
from Server import db


'''
----------------------------------------------------------------------
Table-Base_Data 實作區塊 
----------------------------------------------------------------------
'''
class Base_Data(db.Model):

    __tablename__ = 'base_data'  # 請注意不能大寫，不然migrate在MySQL部份操作會出問題

    BASE_ID = Column(Integer, primary_key=True, autoincrement=True)

    Base_Text = Column(Text(), nullable=False)

    Base_Text2 = Column(String(20), nullable=True)

    Base_Num = Column(Integer , nullable=True)

    InertDate = Column(DateTime(), nullable=False)


'''
----------------------------------------------------------------------
'''

