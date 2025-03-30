from fastapi import Query, Depends
from src.database import session_dep, get_redis_client
from src.utilities import generic_json_response
from src.constants import ResponseConstants, RedisConstants
from sqlalchemy.future import select
from src.cases.models import CaseModel
from src.admin.schemas import CasesCreateSchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class CaseUpdationView:
    '''
        Api collection to create, update or delete cases
    '''
    async def post(self, db: session_dep, request_body : CasesCreateSchema, redis = Depends(get_redis_client)):
        '''
            Post api to add new case
        '''
        try:
            request_body = request_body.model_dump()
            new_case_obj =CaseModel(
                case_number = request_body["case_number"],
                case_title = request_body["case_title"],
                court_name = request_body["court_name"],
                filing_date = request_body["filing_date"],
                upcoming_hearing_date = request_body["upcoming_hearing_date"],
                case_status = request_body["case_status"]
            )

            try:
                db.add(new_case_obj)
                await db.commit()
                await db.refresh(new_case_obj)

            except IntegrityError as err:
                # if case already exist then roll back changes
                await db.rollback()
                return generic_json_response(
                    success = False,
                    status_code = 409,
                    message = ResponseConstants.DATA_ALREADY_EXIST,
                    error = str(err)
                )
            except SQLAlchemyError as err:
                # if database error then rollback
                await db.rollback()
                return generic_json_response(
                    success = False,
                    status_code = 500,
                    message = ResponseConstants.DATABASE_ERROR,
                    error = str(err)
                )
            
            return generic_json_response(
                success = True,
                status_code = 201,
                message = ResponseConstants.NEW_CASE_CREATED_SUCCESSFULLY
            )

        except Exception as err:
            return generic_json_response(
                success = False,
                status_code=500,
                message=ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        
        
    async def patch()
        

case_update_view = CaseUpdationView()