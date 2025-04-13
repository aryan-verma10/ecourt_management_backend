from fastapi import Query, Depends, Response
from src.database import session_dep, get_redis_client
from src.utilities import generic_json_response
from src.constants import ResponseConstants, RedisConstants
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import CaseModel
from src.advocates.models import CaseAdvocatesModel
import json
from .utility import PdfGenerator
from datetime import datetime


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

            case_obj = await db.execute(select(CaseModel).filter(CaseModel.case_number == case_number))
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
        
class CaseDetailsByIdView:
    '''
        Api collection to get all the case details by case number
    '''
    async def get(self, case_number: str, db: session_dep, redis = Depends(get_redis_client)):
        '''
            Get api to get the case details by id
        '''
        try:
            cached_case_obj = await redis.get(RedisConstants.CASE_FULL_DETAILS_BY_CASE_NUMBER+str(case_number))
            if cached_case_obj:
                cached_case_obj = json.loads(cached_case_obj)
                return generic_json_response(
                    success = True,
                    status_code = 200,
                    message = ResponseConstants.CASE_DATA_FETCHED_SUCCESSFULLY,
                    data = cached_case_obj
                )

            base_query = (select(CaseModel)
                          .options(
                              selectinload(CaseModel.case_hearings),
                              selectinload(CaseModel.case_orders),
                              selectinload(CaseModel.case_advocates).selectinload(CaseAdvocatesModel.advocates)
                              )
                          .filter(CaseModel.case_number == case_number)
                          )
            
            cases_objs = await db.execute(base_query)
            cases_objs = cases_objs.scalar_one_or_none()

            if not cases_objs:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.NO_CASES_FOUND
                )
            

            response_body = {
                    "case_id": str(cases_objs.id),
                    "case_number": cases_objs.case_number,
                    "case_title": cases_objs.case_title,
                    "court_name": cases_objs.court_name,
                    "filing_date": cases_objs.filing_date.isoformat() if cases_objs.filing_date else None,
                    "upcoming_hearing_date": cases_objs.upcoming_hearing_date.isoformat() if cases_objs.upcoming_hearing_date else None,
                    "case_status": cases_objs.case_status,
                    "case_hearings_data" : [],
                    "case_orders_data": [],
                    "case_advocates_data": []
                }

            # case_hearing data updating related to this case
            for case_hearing in cases_objs.case_hearings:
                response_body_case_hearing = {
                        "case_hearing_id": case_hearing.id,
                        "hearing_date": case_hearing.hearing_date.isoformat() if case_hearing.hearing_date else None,
                        "judge_name": case_hearing.judge_name,
                        "rival_advocate_name": case_hearing.rival_advocate_name,
                        "hearing_notes": case_hearing.hearing_notes
                    }

                response_body["case_hearings_data"].append(response_body_case_hearing)

            # case orders data updating related to this case
            for case_order in cases_objs.case_orders:
                response_body_case_order = {
                        "case_order_id": case_order.id,
                        "order_date": case_order.order_date.isoformat() if case_hearing.hearing_date else None,
                        "order_details": case_order.order_details
                    }

                response_body["case_orders_data"].append(response_body_case_order)


            # case advocate data updating related to this case
            for case_advocate in cases_objs.case_advocates:
                advocate = case_advocate.advocate
                response_body_case_advocates = {
                        "name": advocate.name,
                        "phone_number": advocate.phone_number,
                        "email": advocate.email,
                        "bar_council_number": advocate.bar_council_number
                    }

                response_body["case_advocates_data"].append(response_body_case_advocates)
                
            # redis data input
            await redis.set(RedisConstants.CASE_FULL_DETAILS_BY_CASE_NUMBER+str(case_number), json.dumps(response_body), ex = 10*24*60*60)
            
            return generic_json_response(
                success = True,
                status_code = 200,
                message = ResponseConstants.CASE_DETAILED_DATA_FETCHED_SUCCESSFULLY,
                data = response_body
            )

        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )
        

class DownloadCaseDetailsView:
    '''
        Download case details pdf
    '''
    async def get(self, case_number: str, db: session_dep, redis = Depends(get_redis_client)):
        '''
            Get api to download the case details
        '''
        try:
            base_query = (select(CaseModel)
                          .options(
                              selectinload(CaseModel.case_hearings),
                              selectinload(CaseModel.case_orders),
                              selectinload(CaseModel.case_advocates).selectinload(CaseAdvocatesModel.advocates)
                              )
                          .filter(CaseModel.case_number == case_number)
                          )
            
            cases_objs = await db.execute(base_query)
            cases_objs = cases_objs.scalar_one_or_none()

            if not cases_objs:
                return generic_json_response(
                    success = False,
                    status_code = 404,
                    message = ResponseConstants.NO_CASES_FOUND
                )
        

            case_info_data =   {                  
                    "case_number": cases_objs.case_number,
                    "case_title": cases_objs.case_title,
                    "court_name": cases_objs.court_name,
                    "filing_date": cases_objs.filing_date.isoformat() if cases_objs.filing_date else None,
                    "upcoming_hearing_date": cases_objs.upcoming_hearing_date.isoformat() if cases_objs.upcoming_hearing_date else None,
                    "case_status": cases_objs.case_status
                }

            case_hearing_data = []
            for data in cases_objs.case_hearings:
                case_hearing_data.append({
                    "hearing_date": data.hearing_date,
                    "judge_name": data.judge_name,
                    "rival_advocate_name": data.rival_advocate_name,
                    "hearing_notes": data.hearing_notes
                })

            case_order_data = []
            for data in cases_objs.case_orders:
                case_order_data.append({
                    "order_date": data.order_date,
                    "order_details": data.order_details
                })

            case_advocate_data = []
            for data in cases_objs.case_advocates:
                case_advocate_data.append({
                    "name": cases_objs.name,
                    "phone_number": data.phone_number,
                    "email": data.email,
                    "bar_council_number": data.bar_council_number
                })

            # pdf generator
            pdf_generator = PdfGenerator()
            pdf_generator.generate_pdf(case_info_data
                                       , case_hearing_data
                                       , case_order_data
                                       , case_advocate_data)

            file_name = case_number
            return Response(
                content = pdf_generator.buffer.read(),
                media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename={file_name}.pdf"
    }
            )


        except Exception as err:
            return generic_json_response(
                success = False,
                status_code = 500,
                message = ResponseConstants.INTERNAL_SERVER_ERROR,
                error = str(err)
            )


find_case_view = FindCaseView()
case_details_by_id_view = CaseDetailsByIdView()
case_details_download_view = DownloadCaseDetailsView()
