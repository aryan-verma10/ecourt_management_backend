from fastapi.responses import JSONResponse


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