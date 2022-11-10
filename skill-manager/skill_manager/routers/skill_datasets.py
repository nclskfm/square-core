import logging
from typing import List

from fastapi import APIRouter

from skill_manager.models import SkillDataset

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skill-datasets")


@router.get(
    "",
    response_model=List[str],
)
async def get_skill_datasets():
    """Returns a list of datasets."""
    datasets = [dataset.value for dataset in SkillDataset]

    logger.debug("get_skill_datasets {datasets}".format(datasets=datasets))
    return datasets
