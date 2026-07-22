from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    project_name: str = Field(min_length=1, max_length=120)


class SectionName(BaseModel):
    """Wspólny kształt dla tworzenia i zmiany nazwy sekcji."""

    section_name: str = Field(min_length=1, max_length=120)


class CabinetInput(BaseModel):
    cabinet_type: str
    width: int = Field(gt=0, le=5000)
    height: int = Field(gt=0, le=5000)
    depth: int = Field(gt=0, le=2000)
    shelves: int = Field(ge=0, le=50)
    fronts: int = Field(ge=0, le=10)
