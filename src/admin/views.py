from fastapi import Query, Depends
from src.database import session_dep, get_redis_client
from src.utilities import generic_json_response, pagination_helper_func, str_to_date_func
from src.constants import ResponseConstants, RedisConstants
from sqlalchemy.future import select
from src.cases.models import CaseModel, CaseHearingModel, CaseOrderModel
from src.admin.schemas import (CasesCreateSchema, CasesUpdateSchema, CaseHearingSchema, CaseHearingUpdateSchema)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import func
from sqlalchemy import or_, bindparam, delete
from sqlalchemy.orm import joinedload
from src.cases.utility import CaseStatus
import math
import json


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
                filing_date = str_to_date_func(request_body["filing_date"]),
                upcoming_hearing_date = str_to_date_func(request_body["upcoming_hearing_date"]),
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
        

    async def get(self, db: session_dep, filter: str = Query(None), page: int = Query(1), limit: int = Query(10)):
        '''
            Get api to get the data of all the cases [No cache only pagination]
        '''
        try:
            offset = (page-1)*limit

            base_query = select(CaseModel.id)
            # if filter present
            if filter:
                if filter.lower() in {status.value for status in CaseStatus}:
                    base_query = base_query.filter(CaseModel.case_status == filter)

                else:
                    base_query = base_query.filter(
                        or_(
                            CaseModel.case_number.ilike(bindparam("filter_value")),
                            CaseModel.case_title.ilike(bindparam("filter_value")),
                        )
                    ).params(filter_value = f"%{filter}%", filter_value_exact = filter)


            final_query = (select(
                CaseModel,
                func.count(CaseModel.id).over().label("total_count")
            ).filter(CaseModel.id.in_(base_query))
            .order_by(CaseModel.created_at)
            .offset(offset)
            .limit(limit))


            cases_objs = await db.execute(final_query)
            
            cases_objs = cases_objs.all()

            if not cases_objs:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.NO_CASES_FOUND
                )
            
            response_body_list = []
            total_enteries = None

            for case_obj, total_count in cases_objs:
                total_enteries = total_count

                response_body = {
                    "case_id": str(case_obj.id),
                    "case_number": case_obj.case_number,
                    "case_title": case_obj.case_title,
                    "court_name": case_obj.court_name,
                    "filing_date": case_obj.filing_date.isoformat(),
                    "upcoming_hearing_date": case_obj.upcoming_hearing_date.isoformat(),
                    "case_status": case_obj.case_status,
                    "created_at": case_obj.created_at.isoformat()
                }        

                response_body_list.append(response_body)

            total_pages = math.ceil(total_enteries/limit)

            page_iterations_dict = pagination_helper_func(total_pages, page)

            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.ALL_CASES_DATA_FETCHED_SUCCESSFULLY,
                data = {"cases_data": response_body_list, "pagination": page_iterations_dict}
            )
        
        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        


    async def patch(self, db: session_dep, case_id: str, request_body : CasesUpdateSchema, redis = Depends(get_redis_client)):
        '''
            Patch api to change the existing case details
        '''
        try:
            request_body = request_body.model_dump(exclude_none=True)
            
            if not request_body:
                return generic_json_response(
                    success = False,
                    status_code = 400,
                    message = ResponseConstants.NO_DATA_TO_UPDATE_PROVIDED
                )

            cases_obj = await db.execute(select(CaseModel).filter(CaseModel.id == case_id))
            case_obj = cases_obj.scalars().first()
            
            if not case_obj:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.CASE_NOT_FOUND
                )
            

            for key, values in request_body.items():
                setattr(case_obj, key, values)

            try:
                await db.commit()
                await db.refresh(case_obj)

            except Exception as err:
                await db.rollback()
                return generic_json_response(
                    success = False,
                    status_code = 500,
                    message = ResponseConstants.DATABASE_ERROR,
                    error = str(err)
                )
            
            # deleting from cache outdated data
            await redis.delete(RedisConstants.CASE_DETAILS+str(case_id))

            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.CASE_DATA_UPDATED_SUCCESSFULLY
            )
            
        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        

# incomplete as post is needed before it
class CaseUpdationByIdView:
    '''
        Api collection by Id case summary and changes
    '''
    async def get(self, case_id: str, db: session_dep, redis = Depends(get_redis_client)):
        try:
            base_query = (select(CaseModel)
                          .options(
                              joinedload(CaseModel.case_hearings),
                              joinedload(CaseModel.case_orders),
                              joinedload(CaseModel.case_advocates)
                              )
                          .filter(CaseModel.id == case_id)
                          )
            
            cases_objs = await db.execute(base_query)
            
            print("cases_objs->", cases_objs)

            return {"hello", "world"}
        
        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )


class CaseHearingUpdateByIdViews:
    '''
        Api collection to update case hearing data or add new one
    '''
    async def post(self, db: session_dep, request_body: CaseHearingSchema, redis = Depends(get_redis_client)):
        try:
            request_body = request_body.model_dump()

            case_hearing_obj = CaseHearingModel(
                case_id = request_body["case_id"],
                hearing_date = str_to_date_func(request_body["hearing_date"]),
                judge_name = request_body["judge_name"],
                rival_advocate_name = request_body["rival_advocate_name"],
                hearing_notes = request_body["hearing_notes"]
            )

            try:
                db.add(case_hearing_obj)
                await db.commit()
                await db.refresh(case_hearing_obj)

            except Exception as err:
                await db.roll_back()
                return generic_json_response(
                    success = False,
                    status_code = 500,
                    message = ResponseConstants.DATABASE_ERROR,
                    error = str(err)
                )
            
            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.NEW_CASE_HEARING_ENTRY_ADDED_SUCCESSFULLY
            )

        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )


    async def get(self, case_hearing_id: int, db: session_dep, redis = Depends(get_redis_client)):
        try:
            case_hearing_cached = await redis.get(RedisConstants.CASE_HEARING_DETAILS_ADMIN+str(case_hearing_id))

            if case_hearing_cached:
                return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.CASE_HEARING_DATA_FETCHED_SUCCESSFULLY,
                data = json.loads(case_hearing_cached)
            )

            base_query = (select(CaseHearingModel).filter(CaseHearingModel.id == case_hearing_id))
            case_hearing_obj = await db.execute(base_query)
            case_hearing_obj = case_hearing_obj.scalar_one_or_none()

            if not case_hearing_obj:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.CASE_HEARING_NOT_FOUND
                )
            

            response_body = {
                "case_hearing_id": case_hearing_obj.id,
                "case_id": str(case_hearing_obj.case_id),
                "judge_name": case_hearing_obj.judge_name,
                "hearing_date": case_hearing_obj.hearing_date.isoformat(),
                "rival_advocate_name": case_hearing_obj.rival_advocate_name,
                "hearing_notes": case_hearing_obj.hearing_notes,
                "created_at": case_hearing_obj.created_at.isoformat(),
            }

            await redis.set(RedisConstants.CASE_HEARING_DETAILS_ADMIN+str(case_hearing_id), json.dumps(response_body), ex=10*24*60*60)

            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.CASE_HEARING_DATA_FETCHED_SUCCESSFULLY,
                data = response_body
            )

        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
    

    async def put(self, case_hearing_id: int, request_body: CaseHearingUpdateSchema, db: session_dep, redis = Depends(get_redis_client)):
        '''
            Patch api to change data in case_hearing model
        '''
        try:
            request_body = request_body.model_dump(exclude_none=True)

            if not request_body:
                return generic_json_response(
                    success = False,
                    status_code = 400,
                    message = ResponseConstants.REQUEST_DATA_EMPTY
                )
            
            case_hearing_obj = await db.execute(select(CaseHearingModel).filter(CaseHearingModel.id == case_hearing_id))
            case_hearing_obj = case_hearing_obj.scalar_one_or_none()

            if not case_hearing_obj:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.CASE_HEARING_NOT_FOUND
                )
            
            
            for key, value in request_body.items():
                setattr(case_hearing_obj, key, value)


            try:
                await db.commit()
                await db.refresh(case_hearing_obj)
                await redis.delete(RedisConstants.CASE_HEARING_DETAILS_ADMIN+str(case_hearing_id))


            except Exception as err:
                await db.roll_back()
                return generic_json_response(
                    success = False,
                    status_code = 500,
                    message = ResponseConstants.DATABASE_ERROR,
                    error = str(err)
                )
            
            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.CASE_HEARING_DATA_UPDATED_SUCCESSFULLY
            )
        
        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        
    async def delete(self, case_hearing_id, db: session_dep, redis = Depends(get_redis_client)):
        '''
            Delete api to delete a case hearing
        '''
        try:
            case_hearing_obj = await db.execute(CaseHearingModel, case_hearing_id)

            if not case_hearing_obj:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.CASE_HEARING_NOT_FOUND
                )
            
            try:
                await db.delete(case_hearing_obj)
                await db.commit()

                return generic_json_response(
                    success = False,
                    status_code = 200,
                    message = ResponseConstants.CASE_HEARING_DELETED_SUCCESSFULLY
                )

            except Exception as err:
                await db.rollback()
                return generic_json_response(
                    success = False,
                    status_code = 500,
                    message = ResponseConstants.DATABASE_ERROR,
                    error = str(err)
                )

        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        

case_update_view = CaseUpdationView()
case_hearing_update_view = CaseHearingUpdateByIdViews()
