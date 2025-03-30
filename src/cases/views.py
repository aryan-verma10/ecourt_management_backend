from fastapi import Query, Depends
from src.database import session_dep, get_redis_client
from src.utilities import generic_json_response
from src.constants import ResponseConstants, RedisConstants
from sqlalchemy.future import select
from .models import CaseModel as cases
import json


class FindCaseView:
    '''
        API collection to find the case details
    '''
    async def get(self, db: session_dep, case_number: str = Query(), redis = Depends(get_redis_client)):
        '''
            Get api to get case major details
        '''
        try:
            cached_case_obj = await redis.get(RedisConstants.CASE_DETAILS+case_number)
            
            # cached data of case
            if cached_case_obj:
                return generic_json_response(
                    success = True,
                    status_code = 200,
                    message = ResponseConstants.CASE_DATA_FETCHED_SUCCESSFULLY,
                    data = json.loads(cached_case_obj)
                )

            case_obj = await db.execute(select(cases).filter(cases.case_number == case_number))
            case_obj = case_obj.scalar_one_or_none()

            if not case_obj:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.CASE_NOT_FOUND
                )
            
            response_body = {
                "id": case_obj.id,
                "case_number": case_obj.case_number,
                "case_title": case_obj.case_title,
                "court_name": case_obj.court_name,
                "case_filing_date": case_obj.filing_date,
                "upcoming_hearing_date": case_obj.upcoming_hearing_date,
                "case_status": case_obj.case_status
            }

            # cached for 10 days
            await redis.set(RedisConstants.CASE_DETAILS+str(case_number), json.dumps(response_body), ex=864000)
            
            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.CASE_DATA_FETCHED_SUCCESSFULLY,
                data = response_body
            )
        

        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        


find_case_view = FindCaseView()