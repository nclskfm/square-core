import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Request
from square_auth.auth import Auth

from evaluator.evaluator import mongo_client
from evaluator.evaluator.core.dataset_handler import (
    DatasetDoesNotExistError,
    DatasetHandler,
)
from evaluator.evaluator.models import Dataset, DataSet
from evaluator.evaluator.mongo.mongo_client import MongoClient
from evaluator.evaluator.routers import client_credentials
from evaluator.evaluator.routers.evaluator import get_dataset_metadata

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset")
auth = Auth()

valid_skill_type = {
    "multiple-choice": "multiple-choice QA",
    "extractive-qa": "extractive-qa",
}


@router.post("", status_code=201)
async def create_dataset(
    *,
    dataset: Dataset = Body(
        examples={
            "multiple_Choice_qa": {
                "summary": "Multiple-Choice sample",
                "description": "Dataset for Multiple-Choice question answering",
                "value": {
                    "dataset_name": "commensense_qa",
                    "skill_type": "multiple-choice",
                    "metric": "accuracy",
                    "mapping": {
                        "id": "id",
                        "question": "question",
                        "choices": ["choice.text"],
                        "answer_index": "1",
                    },
                },
            },
            "extractive_qa": {
                "summary": "Extractive sample",
                "description": "Dataset for Extractive question answering",
                "value": {
                    "dataset_name": "quoref",
                    "skill_type": "extractive-qa",
                    "metric": "squad",
                    "mapping": {
                        "id": "id",
                        "question": "question",
                        "context": "context",
                        "answers": ["answers.text"],
                    },
                },
            },
        },
    ),
):
    # check if the skill-type is not empty
    # download the dataset and check if the dataset_name skill-type and metric exist on huggingface
    logger.debug(f"dataset object: {dataset}")
    try:
        dataset_handler = DatasetHandler()
        dataset_downloaded = dataset_handler.download_dataset(dataset.dataset_name)

    except Exception as exception:
        raise HTTPException(
            404,
            f"The Name of the dataset : {dataset.dataset_name} not found on huggingface!",
        )

    # Load the metric from HuggingFace
    try:
        load(dataset.metric)
    except FileNotFoundError:
        raise HTTPException(
            404, f"Metric with name: {dataset.metric} not found on Huggingface"
        )

    # validate the skill_type if the skill_type
    if dataset.skill_type != valid_skill_type[dataset.skill_type]:
        raise HTTPException(
            404,
            f"skill_type: {dataset.skill_type} is not supported for our case!",
        )

        # Check if the dataset exist on the database, when yes, the item muss not be added
    if mongo_client.client.evaluator.datasets.count_documents(
        {"dataset_name": dataset.dataset_name}
    ):
        raise HTTPException(
            200, f"dataset: {dataset.dataset_name} exist on the database "
        )

    else:

        mongo_client.client.evaluator.datasets.insert_one(dataset.mongo())
        # Download the dataset from
        dataset_handler.download_dataset(dataset.dataset_name)
        m = f"Dataset {dataset.dataset_name} has been added to the database!"
        raise HTTPException(200, m)


@router.get("/{dataset_name}", status_code=200)
async def get_dataset(
    dataset_name: str,
):
    # get the database
    # get collection and find dataset_name on the collection

    try:
        # check if the item exist
        if mongo_client.client.evaluator.datasets.count_documents(
            {"dataset_name": dataset_name}
        ):
            dataset = Dataset.from_mongo(
                mongo_client.client.evaluator.datasets.find_one(
                    {"dataset_name": dataset_name}
                )
            )
            raise HTTPException(200, f"Get dataset: {dataset.dataset_name}")

        else:
            m = f"Dataset_name: {dataset_name} not exist on the database collection!"
            raise HTTPException(404, m)

    except ValueError as e:
        msg = f"Dataset_name: {dataset_name} not found; Error: {e}"
        raise HTTPException(404, msg)


@router.put("", status_code=200)
async def update_dataset(
    dataset: Dataset = Body(
        examples={
            "multiple_Choice_qa": {
                "summary": "Multiple-Choice sample",
                "description": "Dataset for Multiple-Choice question answering",
                "value": {
                    "dataset_name": "commensense_qa",
                    "skill_type": "multiple-choice",
                    "metric": "accuracy",
                    "mapping": {
                        "id": "id",
                        "question": "question",
                        "choices": ["choice.text"],
                        "answer_index": "1",
                    },
                },
            },
            "extractive_qa": {
                "summary": "Extractive sample",
                "description": "Dataset for Extractive question answering",
                "value": {
                    "dataset_name": "quoref",
                    "skill_type": "extractive-qa",
                    "metric": "squad",
                    "mapping": {
                        "id": "id",
                        "question": "question",
                        "context": "context",
                        "answers": ["answers.text"],
                    },
                },
            },
        },
    ),
):
    dataset_handler = DatasetHandler()
    # validate the skill_type if the skill_type
    if dataset.skill_type != valid_skill_type[dataset.skill_type]:
        raise HTTPException(
            404,
            f"skill_type: {dataset.skill_type} is not supported for our case ",
        )

    # Load the metric from HuggingFace
    try:
        # check if the metric exist on huggingface, when not exist raise exception
        load(dataset.metric)
    except FileNotFoundError:
        raise HTTPException(
            404, f"Metric with name: {dataset.metric} not found on Huggingface"
        )

    # check if the dataset_name exist on huggingface
    try:
        dataset_handler.download_dataset(dataset.dataset_name)

    except Exception as exception:
        raise HTTPException(
            404,
            f"The Name of the dataset : {dataset.dataset_name} not found! Error {exception}",
        )

    # check if the dataset_name exist on the database
    try:
        if mongo_client.client.evaluator.datasets.find_one(
            {"dataset_name": dataset.dataset_name}
        ):
            myquery = {"dataset_name": dataset.dataset_name}
            new_value = {
                "$set": {
                    "skill_type": dataset.skill_type,
                    "metric": dataset.metric,
                    "mapping": {
                        "id": dataset.mapping.id,
                        "question": dataset.mapping.question,
                        "context": dataset.mapping.context,
                        "answers": dataset.mapping.answers,
                    },
                }
            }
            mongo_client.client.evaluator.datasets.update_one(myquery, new_value)
            # download the dataset from hugging_face
            dataset_handler.get_dataset(dataset.dataset_name)
            msg = f" Dataset: {dataset.dataset_name} has been updated"
            raise HTTPException(200, msg)
        else:
            raise HTTPException(
                404, f"Dataset: {dataset.dataset_name} not found on the database!"
            )

    except Exception as exception:
        msg = f"Error: {exception}"
        raise HTTPException(404, msg)


@router.delete(
    "/{dataset_name}",
    status_code=200,
)
async def delete_dataset(dataset_name: str):
    try:
        dataset_handler = DatasetHandler()
        dataset_handler.remove_dataset(dataset_name)

        # delete dataset from festplatte and remove to the database
        mongo_client.client.evaluator.datasets.delete_one(
            {"dataset_name": dataset_name}
        )
        raise HTTPException(
            200, f"Dataset {dataset_name} has been deleted on the database"
        )
    except Exception as e:
        msg = f"Dataset_name: {dataset_name} does not found! error {e}"
        raise HTTPException(404, msg)


async def validate_mapping_and_skill_type(dataset: Dataset):
    if dataset.skill_type not in SUPPORTED_SKILL_TYPES.keys():
        raise HTTPException(
            400,
            f'Skill type {dataset.skill_type} not supported! Please use one of the following skill types: {", ".join(SUPPORTED_SKILL_TYPES.keys())}',
        )
    try:
        SUPPORTED_SKILL_TYPES[dataset.skill_type].parse_obj(dataset.mapping)
    except ValidationError as error:
        raise HTTPException(
            400,
            f"Mapping and  skill type {dataset.skill_type} does not match! Error: {error.errors}",
        )
