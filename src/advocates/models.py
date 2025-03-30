from src.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, UUID
from sqlalchemy.orm import relationship
import uuid

# advocates details
class AdvocateModel(Base):
    '''
        Advocate model for advocate details
    '''
    __tablename__ = "advocate_details"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String(14), nullable=False, unique=True)
    email = Column(String, nullable=True)
    bar_council_number = Column(String, nullable=False, unique=True)

    #relations
    case_advocates = relationship("CaseAdvocatesModel", back_populates="advocates")


class CaseAdvocatesModel(Base):
    '''
        Advocate details working on which case
    '''
    __tablename__ = "case_advocates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    advocate_id = Column(UUID(as_uuid=True), ForeignKey("advocate_details.id", ondelete="CASCADE"), nullable=False)


    #relations
    cases = relationship("CaseModel", back_populates="case_advocates")
    advocates = relationship("AdvocateModel", back_populates="case_advocates")