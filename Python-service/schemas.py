from pydantic import BaseModel
from typing import Optional

class StudentProfile(BaseModel):
    id: int
    name: str
    email: str
    systemAccess: Optional[bool] = False
    phone: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    admissionDate: Optional[str] = None
    classe: Optional[str] = None  # "class" is reserved in Python
    section: Optional[str] = None
    roll: Optional[int] = None
    reporterName: Optional[str] = None
    fatherName: Optional[str] = None
    fatherPhone: Optional[str] = None
    motherName: Optional[str] = None
    motherPhone: Optional[str] = None
    guardianName: Optional[str] = None
    guardianPhone: Optional[str] = None
    relationOfGuardian: Optional[str] = None
    currentAddress: Optional[str] = None
    permanentAddress: Optional[str] = None

    class Config:
        populate_by_name = True

    @classmethod
    def from_api(cls, data: dict) -> "StudentProfile":
        """Map raw API response to StudentProfile."""
        data["classe"] = data.pop("class", None)
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})