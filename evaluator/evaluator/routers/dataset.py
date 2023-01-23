import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Request
from square_auth.auth import Auth

from evaluator import mongo_client
from evaluator.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.models import Dataset
from evaluator.mongo.mongo_client import MongoClient
from evaluator.routers import client_credentials
from evaluator.routers.evaluator import get_dataset_metadata

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset")
auth = Auth()


@router.post("", status_code=201)
async def create_dataset(
    *,
    dataset: Dataset = Body(
        examples={
            "multiple_Choice_qa": {
                "summary": "Multiple-Choice sample",
                "description": "for Multiple-Choice Dataset",
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
                "description": "for Extractive Dataset",
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

    dataset_handler = DatasetHandler
    dataset_downloaded = dataset_handler.download_dataset(dataset.dataset_name)

    if dataset_downloaded.name != dataset.dataset_name:
        raise HTTPException(
            400,
            f"skill-type of dataset: {dataset.dataset_name} does not exist on the huggingface ",
        )
    # check if the skill-type of dataset exist on huggingface

    if dataset_downloaded.skill_type != dataset.skill_type:
        raise HTTPException(
            400,
            f"skill_type of dataset: {dataset.dataset_name} does not exist on the huggingface ",
        )
    # check if the metric of dataset exist on huggingface
    if dataset_downloaded.metric != dataset.metric:
        raise HTTPException(
            400,
            f"metric of dataset: {dataset.dataset_name} does not exist on the huggingface ",
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
        dataset_handler = DatasetHandler
        dataset_handler.get_dataset(dataset.dataset_name)

        logger.info(f"Dataset {dataset.dataset_name} has been added to the database.")
        m = f"Dataset {dataset.dataset_name} has been added to mongo DB!"
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
            raise HTTPException(200, f"get dataset: {dataset}")

        else:
            m = f"Dataset_name: {dataset_name} not exist on the database collection!"
            raise HTTPException(400, m)

    except ValueError as e:
        msg = f"Dataset_name: {dataset_name} not found; Error: {e}"
        raise HTTPException(404, msg)


@router.put(
    "/{dataset_name}/{skill_type}/{metric}",
    status_code=200,
)
async def update_dataset(dataset_name: str, skill_type: str, metric: str):
    # check if the dataset_name exist on the collection mongodb
    try:
        # check if the skill-type is not empty
        # download the dataset and check if the dataset_name skill-type and metric exist on huggingface

        dataset_handler = DatasetHandler
        dataset_downloaded = dataset_handler.download_dataset(dataset.dataset_name)

        if dataset_downloaded.name != dataset.dataset_name:
            raise HTTPException(
                400,
                f"skill-type of dataset: {dataset.dataset_name} does not exist on the huggingface ",
            )
        # check if the skill-type of dataset exist on huggingface

        if dataset_downloaded.skill_type != dataset.skill_type:
            raise HTTPException(
                400,
                f"skill_type of dataset: {dataset.dataset_name} does not exist on the huggingface ",
            )
        # check if the metric of dataset exist on huggingface
        if dataset_downloaded.metric != dataset.metric:
            raise HTTPException(
                400,
                f"metric of dataset: {dataset.dataset_name} does not exist on the huggingface ",
            )

        # check if the dataset_name exist
        if mongo_client.client.evaluator.datasets.find_one(
            {"dataset_name": dataset_name}
        ):
            myquery = {"dataset_name": dataset_name}
            new_value = {"$set": {"skill-type": skill_type, "metric": metric}}
            mongo_client.client.evaluator.datasets.replace_one(myquery, new_value)

            # download the dataset from hugging_face
            dataset_handler = DatasetHandler
            dataset_handler.get_dataset(dataset_name)
            logger.info(
                f"Dataset_name {dataset_name} has been updated on the database."
            )

            m = f"Dataset_name: {dataset_name} has be updated"
            raise HTTPException(200, m)

    except ValueError as e:
        msg = f" The dataset_name: {dataset_name} cannot be updated; Error: {e}!"
        raise HTTPException(400, msg)

    return dataset_name


@router.delete(
    "/{dataset_name}",
    status_code=200,
)
async def delete_dataset(dataset_name: str):

    # check if dataset_name exist on the database
    try:
        if mongo_client.client.evaluator.datasets.count_documents(
            {"dataset_name": dataset_name}
        ):
            # delete dataset from festplatte and remove to the database
            dataset_handler = DatasetHandler
            dataset_handler.remove_dataset(dataset_name)

            mongo_client.client.evaluator.datasets.delete_one(
                {"dataset_name": dataset_name}
            )
            raise HTTPException(
                200, f"Dataset {dataset_name} has been deleted on the database"
            )

        else:
            logger.debug(f" Dataset_name not exist")
    except ValueError as e:
        msg = f"Dataset_name: {dataset_name} does not found; Error: {e}"
        logger.error(msg)
        raise HTTPException(404, msg)

    return f"dataset_name: {dataset_name}"
