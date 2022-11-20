from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from evaluator.mongo.mongo_model import MongoModel
from evaluator.mongo.py_object_id import PyObjectId


class Example(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    name: str = Field(..., description="Test name.")
    something: str = Field(..., description="Something. Something.")

    class Config:
        schema_extra = {
            "example": {
                "name": "My Example",
                "something": "Something something.",
            }
        }


class ReferenceAnswer(BaseModel):
    answer_start: List[int] = Field(...)
    text: List[str] = Field(...)


class Prediction(BaseModel):
    text: str = Field(...)
    no_answer_probability: float = Field(...)


class DataPoint(BaseModel):
    id: str = Field(...)
    context: str = Field(...)
    question: str = Field(...)
    reference_answers: Optional[ReferenceAnswer] = Field(...)
    prediction: Optional[Prediction] = Field(...)


class DatasetResult(MongoModel):
    _id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    skill_id: PyObjectId = Field(
        ..., description="Identifier of the skill that generated the prediction."
    )
    dataset_name: str = Field(..., description="Name of the dataset")
    dataset_last_updated_at: datetime = Field()
    data_points: List[DataPoint] = Field(
        ...,
        description="Both the reference data and the prediction for each datapoint of the dataset",
    )
    metrics: Optional[dict] = Field(...)
