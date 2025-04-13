from pydantic import BaseModel
from datetime import date
from src.cases.utility import CaseStatus
from typing import Optional


class CasesCreateSchema(BaseModel):
    '''
        Request body to create new case created
    '''
    case_number : str
    case_title : str
    court_name : str
    filing_date : date | None = None
    upcoming_hearing_date : date | None = None
    case_status : CaseStatus | None = None


class CasesUpdateSchema(BaseModel):
    '''
        Request body to update new data
    '''
    case_number : Optional[str] = None
    case_title : Optional[str] = None
    court_name : Optional[str] = None
    filing_date : Optional[str] = None
    upcoming_hearing_date : Optional[str] = None
    case_status : Optional[str] = None


class CaseHearingSchema(BaseModel):
    '''
        Request body to add new case hearing
    '''
    case_id : str
    hearing_date : str
    judge_name : Optional[str] = None
    rival_advocate_name: Optional[str] = None
    hearing_notes: Optional[str] = None


class CaseHearingUpdateSchema(BaseModel):
    '''
        Request body to update the case hearing
    '''
    hearing_date : Optional[str] = None
    judge_name : Optional[str] = None
    rival_advocate_name : Optional[str] = None
    hearing_notes : Optional[str] = None


class CaseOrderSchema(BaseModel):
    case_id : str
    order_date : str
    order_details : str
    