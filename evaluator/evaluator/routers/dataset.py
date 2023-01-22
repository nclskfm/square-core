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
dataset_item_type = "dataset"
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
    logger.debug(f"post dataset: {dataset}")

    if mongo_client.client.evaluator.datasets.count_documents(
        {"dataset_name": dataset.dataset_name}
    ):
        logger.debug(f"The dataset_name exist on the database!")
        return {f"dataset: {dataset.dataset_name} exist on the database "}

    else:
        if dataset.dataset_name == "quoref":
            dataset_mapping = {
                "dataset_name": dataset.dataset_name,
                "skill-type": dataset.skill_type,
                "metric": dataset.metric,
                "mapping": {
                    "id": dataset.mapping.id,
                    "question": dataset.mapping.question,
                    "context": dataset.mapping.context,
                    "answers": dataset.mapping.answers,
                },
            }
            logger.debug(f"extractive dataset_name: {dataset.dataset_name}")
            mongo_client.client.evaluator.datasets.insert_one(dataset_mapping)
            return {f"Dataset {dataset} has been added to mongo DB!"}

        elif dataset.dataset_name == "commensense_qa":
            dataset_mapping = {
                "dataset_name": dataset.dataset_name,
                "skill-type": dataset.skill_type,
                "metric": dataset.metric,
                "mapping": {
                    "id": dataset.mapping.id,
                    "question": dataset.mapping.question,
                    "choices": dataset.mapping.choices,
                    "answer_index": dataset.mapping.answer_index,
                },
            }
            logger.debug(f" multiple-choice dataset_mapping: {dataset_mapping}")

            mongo_client.client.evaluator.datasets.insert_one(dataset_mapping)
            return {f"Dataset {dataset.dataset_name} has been added to mongo DB!"}

        else:
            return {f"Unknown dataset!"}


@router.get("/{dataset_name}", status_code=200)
async def get_dataset(
    dataset_name: str,
):
    # get the database
    # get collection and find dataset_name on the collection

    logger.debug(f"GET dataset: dataset_name= {dataset_name}")
    try:
        db_dataset_name = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )
        if db_dataset_name is not None:
            logger.debug(f"Dataset_name exist on datasets collection!")
            for item in db_dataset_name:

                if str(item["dataset_name"]) == str("commonsense_qa"):

                    return {
                        "dataset_name": item["dataset_name"],
                        "skill-type": item["skill-type"],
                        "metric": item["metric"],
                        "mapping": {
                            "id-column": item["mapping"]["id-column"],
                            "question-column": item["mapping"]["question-column"],
                            "choices-columns": item["mapping"]["choices-columns"],
                            "choices-key-mapping-column": item["mapping"][
                                "choices-key-mapping-column"
                            ],
                            "answer-index-column": item["mapping"][
                                "answer-index-column"
                            ],
                        },
                    }
                elif str(item["dataset_name"]) == str("quoref"):
                    return {
                        "dataset_name": item["dataset_name"],
                        "skill-type": item["skill-type"],
                        "metric": item["metric"],
                        "mapping": {
                            "id-column": item["mapping"]["id-column"],
                            "question-column": item["mapping"]["question-column"],
                            "context-column": item["mapping"]["context-column"],
                            "answer-text-column": item["mapping"]["answer-text-column"],
                        },
                    }
                else:
                    return f" Undefined dataset_name"
        else:
            return "Dataset_name not exist on the datasets collection!"

    except ValueError as e:
        msg = f"Dataset_name: {dataset_name} not found; Error: {e}"
        logger.debug(msg)
        raise HTTPException(404, msg)


@router.put(
    "/{dataset_name}/{skill_type}/{metric}",
    status_code=200,
)
async def update_dataset(dataset_name: str, skill_type: str, metric: str):
    logger.debug("put dataset")
    metadata = get_dataset_metadata(dataset_name=dataset_name)

    # check if the dataset_name exist on the collection mongodb
    try:
        dataset_result = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )
    except ValueError as e:
        msg = f" The dataset_name: {dataset_name} not be found; Error: {e}!"
        logger.error(msg)
        raise HTTPException(400, m)
    for dataset_item in dataset_result:
        if dataset_item["dataset_name"] is not None:
            try:
                myquery = {"dataset_name": dataset_item["dataset_name"]}
                new_value = {"$set": {"skill-type": skill_type, "metric": metric}}
                mongo_client.client.evaluator.datasets.update_one(myquery, new_value)

                logger.debug(f"Dataset_name {dataset_name} is updated from mongodb!")
                return f"Dataset_name: {dataset_item['dataset_name']} has be update"
            except ValueError as e:
                msg = (
                    f" The dataset_name: {dataset_name} cannot be inserted; Error: {e}!"
                )
                logger.error(msg)
                raise HTTPException(400, msg)
    return dataset_name


@router.delete(
    "/{dataset_name}",
    status_code=200,
)
async def delete_dataset(dataset_name: str):
    logger.debug("Delete dataset_name on mongodb")

    # check if dataset_name exist on the database
    try:
        result_db = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )
        logger.debug(f"db_dataser_name = {result_db}")
    except ValueError as e:
        msg = f"Datasetr_name: {dataset_name} does not found; Error: {e}"
        logger.error(msg)
        raise HTTPException(404, msg)

    for item in result_db:
        if item["dataset_name"] is not None:

            try:
                mongo_client.client.evaluator.datasets.delete_one(
                    {"dataset_name": dataset_name}
                )
                logger.debug(f"Dataset_name {dataset_name} is deleted from mongodb!")
            except ValueError as e:
                msg = f"Dataset_name: {dataset_name} cannot be deleted on the database"
                logger.error(msg)
                raise HTTPException(404, msg)
            return f"dataset_name: {dataset_name} has be deleted!"

    return f"dataset_name: {dataset_name} not exist on the Database!"
