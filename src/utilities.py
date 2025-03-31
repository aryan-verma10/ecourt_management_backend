from fastapi.responses import JSONResponse
from datetime import datetime


def generic_json_response(success: bool=True, status_code: int=200, message="", data="", error=""):
    '''
        generic response for all the apis
    '''
    content = {
        "success": success,
        "status_code": status_code,
        "message": message,
        "data": data,
        "error": error
    }
    return JSONResponse(content=content, status_code=status_code)


def pagination_helper_func(total_pages, page):
    '''
        Helper function to pagination
    '''
    return {
                "current_page": page,
                "previous_page": None if page <= 1 else page-1,
                "next_page": None if page >= total_pages else page+1, 
                "total_pages": total_pages
            }

def str_to_date_func(date_str):
    '''
        Helper function to convert str to date
    '''
    if not date_str:
        return None
    
    date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
    return date_obj