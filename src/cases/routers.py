from fastapi import APIRouter
from .views import find_case_view, case_details_by_id_view, case_details_download_view


router = APIRouter(prefix="/cases")

router.add_api_route("/find-case", find_case_view.get, methods=["GET"])
router.add_api_route("/case-details", case_details_by_id_view.get, methods=["GET"])
router.add_api_route("/case-details/download", case_details_download_view.get, methods=["GET"])