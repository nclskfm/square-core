from fastapi import APIRouter

from skill_manager.routers.health import router as health_router
from skill_manager.routers.skill import router as skill_router
from skill_manager.routers.skill_types import router as skill_types_router
from skill_manager.routers.skill_datasets import router as skill_datasets_router

router = APIRouter()

router.include_router(health_router)
router.include_router(skill_router)
router.include_router(skill_types_router)
router.include_router(skill_datasets_router)
