import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Request
from square_auth.auth import Auth

from evaluator.app import mongo_client

# from evaluator.app.mongo import mongo_client
from evaluator.app.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.app.core.task_helper import dataset_exists, metric_exists
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
            f"skill_type: {dataset.skill_type} is not supported! Please try the following skill_type: {VALID_SKILL_TYPES.keys()} ",
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
        mongo_client.client.evaluator.datasets.insert_one(dataset.mongo())
        # Download the dataset from
        m = (
            f"Dataset {dataset.dataset_name}; skill_type: {dataset.skill_type};"
            f" metric: {dataset.metric} has been added to the database!"
        )
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
            raise HTTPException(
                200,
                f"Get dataset: {dataset.dataset_name} skill_type: {dataset.skill_type}"
                f" metric: {dataset.metric} mapping: {dataset.mapping} ",
            )

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

        if dataset.skill_type == list(VALID_SKILL_TYPES.keys())[0]:

            dataset_mapping = {
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
            mongo_client.client.evaluator.datasets.update_one(myquery, dataset_mapping)
        else:

            dataset_mapping = {
                "$set": {
                    "skill_type": dataset.skill_type,
                    "metric": dataset.metric,
                    "mapping": {
                        "id": dataset.mapping.id,
                        "question": dataset.mapping.question,
                        "choices": dataset.mapping.choices,
                        "choices_key_mapping": dataset.mapping.choices_key_mapping,
                        "answer_index": dataset.mapping.answer_index,
                    },
                }
            }
            mongo_client.client.evaluator.datasets.update_one(myquery, dataset_mapping)

            # download the dataset from hugging_face
            msg = f" Dataset: {dataset.dataset_name} has been updated"
            raise HTTPException(200, msg)
    else:
        raise HTTPException(
            404,
            f"Dataset name: {dataset.dataset_name} cannot found on the database",
        )


@router.delete(
    "/{dataset_name}",
    status_code=200,
)
async def delete_dataset(dataset_name: str):
    # delete dataset from festplatte and remove to the database
    dataset_handler.remove_dataset(dataset_name)
    if mongo_client.client.evaluator.datasets.delete_one(
        {"dataset_name": dataset_name}
    ):
        raise HTTPException(
            200, f"Dataset {dataset_name} has been deleted on the database"
        )
    else:
        msg = f"Dataset_name: {dataset_name} not found!"
        raise HTTPException(404, msg)


async def validate_mapping_and_skill_type(dataset: Dataset):
    if dataset.skill_type not in VALID_SKILL_TYPES.keys():
        raise HTTPException(
            404,
            f'Skill type {dataset.skill_type} not valis! Use the following skill types: {", ".join(VALID_SKILL_TYPES.keys())}',
        )
    try:
        VALID_SKILL_TYPES[dataset.skill_type].parse_obj(dataset.mapping)
    except ValidationError as error:
        raise HTTPException(
            404,
            f"Mapping and  skill type {dataset.skill_type} does not match! Error: {error.errors}",
        )
