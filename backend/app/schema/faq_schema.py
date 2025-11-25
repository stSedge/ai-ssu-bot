from pydantic import BaseModel, ConfigDict

class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQRead(FAQBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
