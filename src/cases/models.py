from src.database import Base
from sqlalchemy import (Column, Integer, String, 
                        UUID, ForeignKey, Date, 
                        Enum, Text)
from sqlalchemy.orm import relationship
import uuid
from .utility import CaseStatus
from src.advocates.models import CaseAdvocatesModel


 # this contains database tables related to cases

class CaseModel(Base):
    '''
        Model related to case
    '''
    __tablename__ = "cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    case_number = Column(String, nullable=False, unique=True)
    case_title = Column(String, nullable=False)
    court_name = Column(String, nullable=False)
    filing_date = Column(Date, nullable=True)
    upcoming_hearing_date = Column(Date, nullable=True)
    case_status = Column(Enum(CaseStatus), default=CaseStatus.PENDING, nullable=False)

    # relationships
    case_hearings = relationship("CaseHearingModel", back_populates="cases")
    case_orders = relationship("CaseOrderModel", back_populates="cases")
    case_advocates = relationship("CaseAdvocatesModel", back_populates="cases")


class CaseHearingModel(Base):
    '''
        Model related to case hearing
    '''
    __tablename__ = "case_hearing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable = False)
    hearing_date = Column(Date, nullable=True)
    judge_name = Column(String, nullable=True)
    rival_advocate_name = Column(String, nullable=True)
    hearing_notes = Column(Text, nullable=True)

    # relationships [ foreign key constraints are only needed when same ref given to table]
    cases = relationship("CaseModel", back_populates="case_hearings")



class CaseOrderModel(Base):
    '''
        Model related to case orders
    '''
    __tablename__ = "case_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    order_date = Column(Date, nullable=False)
    order_details = Column(Text, nullable=False)

    cases = relationship("CaseModel", back_populates="case_orders")

