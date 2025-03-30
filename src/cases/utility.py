from enum import Enum

class CaseStatus(str, Enum):
    '''
        Enum defined for case status
    '''
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
