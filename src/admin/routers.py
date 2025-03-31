from fastapi import APIRouter
from .views import case_update_view, case_hearing_update_view

router = APIRouter(prefix="/admin")


router.add_api_route("/get-cases", case_update_view.get, methods=["GET"])
router.add_api_route("/create-cases", case_update_view.post, methods=["POST"])
router.add_api_route("/update-cases", case_update_view.patch, methods=["PATCH"])
router.add_api_route("/case-hearings", case_hearing_update_view.post, methods=["POST"])
router.add_api_route("/case-hearings", case_hearing_update_view.get, methods=["GET"])
router.add_api_route("/case-hearings", case_hearing_update_view.put, methods=["PUT"])