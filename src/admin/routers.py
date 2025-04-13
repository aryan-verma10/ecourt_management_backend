from fastapi import APIRouter
from .views import (case_update_view, case_hearing_update_view,
                     case_by_id_view, case_order_view)

router = APIRouter(prefix="/admin")


router.add_api_route("/cases", case_update_view.get, methods=["GET"])
router.add_api_route("/cases", case_update_view.post, methods=["POST"])
router.add_api_route("/cases", case_update_view.patch, methods=["PATCH"])
router.add_api_route("/cases/id", case_by_id_view.delete, methods=["DELETE"])
router.add_api_route("/cases/id", case_by_id_view.get, methods=["GET"])
router.add_api_route("/case-hearings", case_hearing_update_view.post, methods=["POST"])
router.add_api_route("/case-hearings", case_hearing_update_view.get, methods=["GET"])
router.add_api_route("/case-hearings", case_hearing_update_view.put, methods=["PUT"])
router.add_api_route("/case-hearings", case_hearing_update_view.delete, methods=["DELETE"])
router.add_api_route("/case-orders", case_order_view.post, methods=["POST"])
