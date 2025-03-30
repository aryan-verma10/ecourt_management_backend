from fastapi import APIRouter
from .views import case_update_view

router = APIRouter(prefix="/admin")

router.add_api_route("/create-cases", case_update_view.post, methods=["POST"])