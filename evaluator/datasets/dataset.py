import logging
from fastapi import Depends, HTTPException, Request
from evaluate import load
from fastapi import APIRouter
from typing import Dict, List
from evaluator.datasets.models import Dataset, DatasetResult
from evaluator.evaluator.core.dataset_handler import DatasetHandler
from bson import ObjectId
from square_auth.auth import Auth
from evaluator.evaluator.core.dataset_handler import DatasetDoesNotExistError
from evaluator.evaluator.routers import client_credentials
from evaluator.evaluator import mongo_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset")
dataset_item_type = 'dataset'
dataset_handler = DatasetHandler()

auth = Auth()


@router.get(
    "/dataset/{dataset_name}",
    name="squad",
    responses={
        200: {
            "model": List[Dataset]
        },
        404: {
            "description": "The dataset could not be found"
        }
    },
)
async def get_datasets():
    """Return list of datasets value."""
    datasets = [data.value for data in Dataset]

    logger.debug("get_datasets: ".format(datasets=datasets))
    return datasets


@router.put(
    "/dataset/{dataset_name}",
    status_code=201,
)
async def put_dataset(

):
    logger.debug("put dataset")


@router.delete(
    "/dataset/{dataset_name}",
    status_code=201,

)
async def delete_dataset(

):
    logger.debug("deleted dataset by name")


@router.post(
    "/dataset/{dataset_name}",
    status_code=201,
)
async def create_dataset(
        request: Request,
        dataset_name: str,
        skill_type: str,
        metric: str,
        mapping: dict,
        dataset_handler: DatasetHandler = Depends(DatasetHandler),
        token: str = Depends(client_credentials),
        token_payload: Dict = Depends(auth),
):
    logger.debug(f"post dataset: {dataset_name}, {skill_type}, {metric}, {mapping} ")

    object_identification = {"dataset_name": ObjectId(dataset_name), "skill_type": ObjectId(skill_type),
                             "metric": ObjectId(metric), "mapping": ObjectId(mapping)}

    # load metric from huggingface
    try:
        metric = load(metric)
    except FileNotFoundError:
        logger.error(f"Metric with name='{metric}' not found")
        raise HTTPException(404, f"Metric with name='{metric}' not found!")

    # load skill_type from mongo database ToDO

    # load dataset
    dataset_metadata = get_dataset_metadata(dataset_name)
    try:
        dataset_metadata = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError:
        logger.error("Dataset does not exist!")
        raise HTTPException(400, "Dataset name does not exist!")

    # map dataset into a generic format

    dataset_result = DatasetResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(dataset_name)
    )
    # Execute dataset post
    dataset_ob = Dataset(dataset_name=dataset_name, skill_type=skill_type, metric=metric, mapping=mapping)

    new_datasets = dataset_result.dataset_name
    new_datasets[dataset_name] = dataset_ob

    mongo_client.client.evaluator.results.replace_one(
        dataset_name, dataset_result.mongo(), upsert=True
    )
    return dataset_ob


def get_dataset_metadata(dataset_name):
    if dataset_name == "squad":
        return {
            "name": "squad",
            "skill-type": "extractive-qa",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
            },
        }
    elif dataset_name == "quoref":
        return {
            "name": "quoref",
            "skill-type": "extractive-qa",
            "metric": "squad",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
            },
        }
    elif dataset_name == "commonsense_qa":
        return {
            "name": "commonsense_qa",
            "skill-type": "multiple-choice",
            "metric": "accuracy",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "choices-columns": ["choices.text"],
                "choices-key-mapping-column": "choices.label",
                "answer-index-column": "answerKey",
            },
        }
    elif dataset_name == "cosmos_qa":
        return {
            "name": "cosmos_qa",
            "skill-type": "multiple-choice",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "choices-columns": ["answer0", "answer1", "answer2", "answer3"],
                "choices-key-mapping-column": None,
                "answer-index-column": "label",
            },
        }
    else:
        logger.error("Unsupported dataset!")
        raise HTTPException(400, "Unsupported dataset!")
