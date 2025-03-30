from fastapi import APIRouter
from src.cases.routers import router as case_router
from src.admin.routers import router as admin_router

router = APIRouter(prefix="/v1")

router.include_router(case_router, tags=["Case"])
router.include_router(admin_router, tags=["admin"])