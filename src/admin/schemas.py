from pydantic import BaseModel
from datetime import date
from src.cases.utility import CaseStatus


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
    
