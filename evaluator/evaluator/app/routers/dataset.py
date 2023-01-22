import logging
from typing import List

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from pydantic import ValidationError

from evaluator.app import mongo_client
from evaluator.app.core.dataset_metadata import (
    DatasetMetadataDoesNotExistError,
    get_dataset_metadata,
)
from evaluator.app.models import SUPPORTED_SKILL_TYPES, DatasetMetadata

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dataset")


@router.get(
    "",
    response_model=List[str],
)
async def get_datasets():
    """Returns a list of supported data sets."""

    results = mongo_client.client.evaluator.datasets.find()
    datasets = [DatasetMetadata.from_mongo(result).name for result in results]
    logger.debug("get_datasets {datasets}".format(datasets=datasets))
    return datasets


@router.get("/{dataset_name}", status_code=200, response_model=DatasetMetadata)
async def get_dataset(dataset_name: str):
    try:
        return get_dataset_metadata(dataset_name)
    except DatasetMetadataDoesNotExistError as error:
        raise HTTPException(404, error.args)


@router.post(
    "",
    status_code=201,
)
async def create_metadata(request: Request, dataset_metadata: DatasetMetadata):
    await validate_mapping_and_skill_type(dataset_metadata)
    datasets = await get_datasets()
    if dataset_metadata.name in datasets:
        raise HTTPException(
            400,
            f"Metadata entry with dataset_name={dataset_metadata.name} already exists! Please use the PUT method to update the entry.",
        )
    result = mongo_client.client.evaluator.datasets.insert_one(dataset_metadata.mongo())
    if result.acknowledged:
        return
    else:
        raise RuntimeError(result.raw_result)


@router.put(
    "",
    status_code=201,
)
async def update_metadata(request: Request, dataset_metadata: DatasetMetadata):
    await validate_mapping_and_skill_type(dataset_metadata)
    datasets = await get_datasets()
    if dataset_metadata.name not in datasets:
        raise HTTPException(
            400,
            f"Metadata entry with dataset_name={dataset_metadata.name} does not exist! Please use the POST method to create the entry.",
        )
    result = mongo_client.client.evaluator.datasets.replace_one(
        {"name": dataset_metadata.name}, dataset_metadata.mongo(), upsert=False
    )
    if result.acknowledged:
        return
    else:
        raise RuntimeError(result.raw_result)


@router.delete(
    "/metadata/{dataset_name}",
    status_code=200,
)
async def delete_metadata(dataset_name: str):
    delete_result = mongo_client.client.evaluator.datasets.delete_one(
        {"name": dataset_name}
    )
    logger.debug(f"delete_metadata: {dataset_name}")
    if delete_result.deleted_count == 1:
        return
    else:
        raise HTTPException(
            404,
            f"Dataset {dataset_name} could not be deleted, because it was not found.",
        )


async def validate_mapping_and_skill_type(dataset_metadata: DatasetMetadata):
    if dataset_metadata.skill_type not in SUPPORTED_SKILL_TYPES.keys():
        raise HTTPException(
            400,
            f'Skill type {dataset_metadata.skill_type} not supported! Please use one of the following skill types: {", ".join(SUPPORTED_SKILL_TYPES.keys())}',
        )
    try:
        SUPPORTED_SKILL_TYPES[dataset_metadata.skill_type].parse_obj(
            dataset_metadata.mapping
        )
    except ValidationError as error:
        raise HTTPException(
            400,
            f"The mapping does not match the skill type {dataset_metadata.skill_type}: {error.errors}",
        )
