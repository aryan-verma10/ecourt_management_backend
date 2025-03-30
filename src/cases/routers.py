from fastapi import APIRouter
from .views import find_case_view


router = APIRouter(prefix="/cases")

router.add_api_route("/find-case", find_case_view.get, methods=["GET"])