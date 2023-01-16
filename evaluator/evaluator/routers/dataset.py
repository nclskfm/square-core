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
    dataset_name: Dataset = Body(
        examples={
            "Multiple-Choicesample": {
                "summary": "Multiple-Choicesample",
                "description": "for Multiple-Choice Dataset",
                "value": {
                    "name": "commensense_qa",
                    "skill_type": "multiple-choice",
                    "metric": "accuracy",
                    "mapping": {
                        "id-column": "id",
                        "question-column": "question",
                        "choice-columns": ["choice.text"],
                        "choices-key-mapping-column": "choices.label",
                        "answer-index-column": "answerkey",
                    },
                },
            },
            "Extractivesample": {
                "summary": "Extractivesample",
                "description": "for Extractive Dataset",
                "value": {
                    "name": "quoref",
                    "skill-type": "extractive-qa",
                    "metric": "squad",
                    "mapping": {
                        "id-column": "id",
                        "question-column": "question",
                        "context-column": "context",
                        "answer-text-column": "answers.text",
                    },
                },
            },
        },
    ),
):
    logger.debug(f"post dataset: dataset_name= {name}")
    dataset_name_exist = mongo_client.client.evaluator.datasets.find(
        {"dataset_name": name}
    )
    logger.debug(f"post anfrage")
    if dataset_name_exist is None:
        logger.debug(f"dataset name is None ")

        if name == "quoref":
            dataset_mapping = {
                "name": name,
                "skill-type": skill_type,
                "metric": metric,
                "mapping": {
                    "id-column": mapping["id-column"],
                    "question-column": mapping["question-column"],
                    "context-column": mapping["context-column"],
                    "answer-text-column": mapping["answer-text-column"],
                },
            }

        elif name == "commensense_qa":
            dataset_mapping = {
                "name": name,
                "skill-type": skill_type,
                "metric": metric,
                "mapping": {
                    "id-column": mapping["id-column"],
                    "question-column": mapping["question-column"],
                    "choice-columns": mapping["choice-columns"],
                    "choices-key-mapping-column": mapping["choices-key-mapping-column"],
                    "answer-index-column": mapping["answer-index-column"],
                },
            }

            dataset_ob = Dataset(
                dataset_name=dataset_name,
                skill_type=skill_type,
                metric=metric,
                mapping=mapping,
            )
            # mongo_client.client.evaluator.datasets.insert_one(dataset_mapping)
            mongo_client.client.evaluator.datasets.insert_one(dataset_mapping)
            logger.debug(f"dataset_name: ", {dataset_mapping})
            return dataset_mapping


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


@router.get(
    "/get_all_dataset/",
    status_code=200,
)
async def get_all_datasets():
    logger.debug("get all Datasets")

    dataset_list = []
    dataset_result = mongo_client.client.evaluator.datasets.find()

    for item in dataset_result:
        logger.debug("item get_all_dataset: ", item)

        dataset_list.append(item["dataset_name"])
        logger.debug("dataset exist on database! ")
        return {"Dataset_name: ", item["dataset_name"]}

    return {"dataset not found"}


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
                    {"dataset_name": item["dataset_name"]}
                )
                logger.debug(
                    f"Dataset_name {item['dataset_name']} is deleted from mongodb!"
                )
            except ValueError as e:
                msg = f"Dataset_name: {dataset_name} cannot be deleted on the database"
                logger.error(msg)
                raise HTTPException(404, msg)
            return f"dataset_name: {item['dataset_name']} has be deleted!"

    return f"dataset_name: {dataset_name} not exist on the Database!"
