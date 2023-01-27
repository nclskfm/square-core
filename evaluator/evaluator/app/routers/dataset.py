import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from square_auth.auth import Auth

from evaluator.app import mongo_client

# from evaluator.app.mongo import mongo_client
from evaluator.app.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.app.core.task_helper import dataset_exists
from evaluator.app.models import VALID_SKILL_TYPES, Dataset
from evaluator.app.routers import client_credentials

dataset_handler = DatasetHandler()
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
                "description": "Dataset for Multiple-Choice question answering",
                "value": {
                    "dataset_name": "cosmos_qa",
                    "skill_type": "multiple-choice",
                    "metric": "accuracy",
                    "mapping": {
                        "id": "id",
                        "question": "question",
                        "choices": ["answer1"],
                        "choices_key_mapping": "key mapping choices",
                        "answer_index": "label",
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
                        "answers": "text answers",
                    },
                },
            },
        },
    ),
):
    # validate the skill_type if the skill_type
    if dataset.skill_type not in VALID_SKILL_TYPES.keys():
        raise HTTPException(
            404,
            f"Skill_type: {dataset.skill_type} is not supported! Try the following skill_type: {VALID_SKILL_TYPES.keys()} are used ",
        )
    # Load the metric from HuggingFace
    try:
        load(dataset.metric)
    except FileNotFoundError:
        raise HTTPException(
            404, f"Metric with name: {dataset.metric} not found on Huggingface"
        )
    if dataset_exists(dataset.dataset_name):
        dataset_handler.get_dataset(dataset.dataset_name)
    else:
        try:
            dataset_handler.download_dataset(dataset.dataset_name)
        except:
            HTTPException(404, "Dataset does not exist on huggingface!")

    # Check if the dataset exist on the database, when yes, the item muss not be added
    if mongo_client.client.evaluator.datasets.count_documents(
        {"dataset_name": dataset.dataset_name}
    ):
        raise HTTPException(
            200, f"dataset: {dataset.dataset_name} already exist on the database "
        )
    else:
        # validate mapping and skill_type
        await validate_mapping_and_skill_type(dataset)
        mongo_client.client.evaluator.datasets.insert_one(dataset.mongo())
        return jsonable_encoder(dataset)


@router.get("/{dataset_name}", status_code=200)
async def get_dataset(
    dataset_name: str,
):
    # check if the item exist
    dataset_handler.get_dataset(dataset_name)
    if (
        dataset := Dataset.from_mongo(
            mongo_client.client.evaluator.datasets.find_one(
                {"dataset_name": dataset_name}
            )
        )
    ) is not None:
        return jsonable_encoder(dataset)
    else:
        m = f"Dataset_name: {dataset_name} not exist on the database collection!"
        raise HTTPException(404, m)


@router.put("", status_code=200)
async def update_dataset(
    dataset: Dataset = Body(
        examples={
            "multiple_Choice_qa": {
                "summary": "Multiple-Choice sample",
                "description": "Dataset for Multiple-Choice question answering",
                "value": {
                    "dataset_name": "cosmos_qa",
                    "skill_type": "multiple-choice",
                    "metric": "accuracy",
                    "mapping": {
                        "id": "id",
                        "question": "question",
                        "choices": ["answer1"],
                        "choices_key_mapping": "key mapping choices",
                        "answer_index": "label",
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
                        "answers": "answers1",
                    },
                },
            },
        },
    ),
):
    # validate the skill_type if the skill_type
    if dataset.skill_type not in VALID_SKILL_TYPES.keys():
        raise HTTPException(
            404,
            f"skill_type: {dataset.skill_type} is not supported! Please try the following skill_type: {VALID_SKILL_TYPES.keys()} ",
        )
    try:
        # check if the metric exist on huggingface, when not exist raise exception
        load(dataset.metric)
    except FileNotFoundError:
        raise HTTPException(404, f"Metric: {dataset.metric} not found on Huggingface")

    if dataset_exists(dataset.dataset_name):
        # check if the dataset_name exist on localstorage
        dataset_handler.get_dataset(dataset.dataset_name)
    else:
        try:
            # if the dataset does not exist local it try to download it
            dataset_handler.download_dataset(dataset.dataset_name)
        except:
            raise HTTPException(
                404,
                f"The Name of the dataset : {dataset.dataset_name} not found on Huggingface!",
            )
        # check if the dataset_name exist on the database
    if mongo_client.client.evaluator.datasets.find_one(
        {"dataset_name": dataset.dataset_name}
    ):
        myquery = {"dataset_name": dataset.dataset_name}
        try:
            await validate_mapping_and_skill_type(dataset)
            dataset_json = jsonable_encoder(dataset)
            mongo_client.client.evaluator.datasets.update_one(
                myquery, {"$set": dataset_json}
            )
            return dataset_json
        except:
            HTTPException(
                404,
                f"Mapping of dataset: {dataset.dataset_name} and skill_type {dataset.skill_type} does not match",
            )
    else:
        raise HTTPException(
            404,
            f"Dataset name: {dataset.dataset_name} cannot be updated, not found!",
        )


@router.delete(
    "/{dataset_name}",
    status_code=200,
)
async def delete_dataset(dataset_name: str):
    # delete dataset from festplatte and remove to the database
    dataset_handler.remove_dataset(dataset_name)
    result_dataset = mongo_client.client.evaluator.datasets.delete_one(
        {"dataset_name": dataset_name}
    )

    if result_dataset.deleted_count == 1:
        return dataset_name
    else:
        msg = f"Dataset_name: {dataset_name} not found!"
        raise HTTPException(404, msg)


async def validate_mapping_and_skill_type(dataset: Dataset):
    try:
        VALID_SKILL_TYPES[dataset.skill_type].parse_obj(dataset.mapping)
    except ValidationError as error:
        raise HTTPException(
            404,
            f"Skill type {dataset.skill_type} and mapping does not match! error {error}",
        )
