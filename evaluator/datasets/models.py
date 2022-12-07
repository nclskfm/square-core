from pydantic import BaseModel, Field
from evaluator.evaluator.mongo.mongo_model import MongoModel


class Dataset(BaseModel):
    dataset_name: str = Field(...)
    skill_type: str = Field(...)
    metric: str = Field(...)
    mapping: dict = Field(...,
                          description="Dictionary of mapping object. The values depend on the respective dastaset.")


class DatasetResult(MongoModel):
    dataset_name: str = Field(..., description="ID of the sample dataset.")
    skill_type: str = Field(..., description="Type of the skill")
    metric: str = Field(..., description="metric")
    mapping: dict = Field(..., description="Dictionary of all mapping objects")
