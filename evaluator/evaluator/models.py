from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from evaluator.mongo.mongo_model import MongoModel
from evaluator.mongo.py_object_id import PyObjectId


class DataSet(str, Enum):
    """Enum for different data sets."""

    CommonSenseQA = "CommonSenseQA"
    CosmosQA = "CosmosQA"
    DROP = "DROP"
    HotpotQA = "HotpotQA"
    MultiRC = "MultiRC"
    NarrativeQA = "NarrativeQA"
    NewsQA = "NewsQA"
    OpenBioASQ = "OpenBioASQ"
    QuAIL = "QuAIL"
    QuaRTz = "QuaRTz"
    Quoref = "Quoref"
    RACE = "RACE"
    SQuAD = "SQuAD"
    Social_IQA = "Social-IQA"
    BoolQ = "BoolQ"


class Prediction(BaseModel):
    id: str = Field(
        ..., description="Identifier of the sample in the respective dataset."
    )
    output: str = Field(
        ...,
        description="The actual output of the model as string. "
        "Could be an answer for QA, an argument for AR or a label for Fact Checking.",
    )
    output_score: float = Field(..., description="The score assigned to the output.")


class PredictionResult(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    skill_id: PyObjectId = Field(
        ..., description="Identifier of the skill that generated the prediction."
    )
    dataset_name: str = Field(..., description="Name of the dataset")
    last_updated_at: datetime = Field()
    calculation_time: float = Field(..., description="Calculation time in seconds")
    predictions: List[Prediction] = Field(...)


class Metric(BaseModel):
    last_updated_at: datetime = Field(...)
    calculation_time: float = Field(..., description="Calculation time in seconds")
    results: dict = Field(
        ...,
        description="Dictionary of calculated results. The values depend on the respective metric.",
    )


class MetricResult(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    prediction_result_id: PyObjectId = Field(
        ..., description="Identifier of the corresponding PredictionResult object"
    )
    metrics: dict = Field(..., description="Dictionary of all Metric objects")
