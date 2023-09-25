from typing import Self, Optional
import os
from pathlib import Path
from bson import ObjectId
from uuid import UUID
from xpyutils import lazy_property

class Document:
    
    def __init__(
            self, 
            filepath: os.PathLike,
            modification_time: Optional[float] = None
        ) -> None:
        
        self._id: Optional[ObjectId] = None
        self._vec_id: Optional[UUID] = None
        self._filepath = Path(filepath).absolute()
        
        # Set modification time
        if modification_time is None:
            self._modification_time = self._filepath.stat().st_mtime
        else:
            self._modification_time = modification_time
    
    def __str__(self) -> str:
        
        return (
            "{{"
            "id: {id}, "
            "vec_id: {vec_id}, "
            "filepath: {filepath}, "
            "modification_time: {modification_time}"
            "}}"
        ).format(
            id=self.id,
            vec_id=self.vec_id.hex,
            filepath=self.filepath,
            modification_time=self.modification_time
        )
        
    def __repr__(self) -> str:
        
        return str(self)
    
    @property
    def id(self) -> Optional[ObjectId]:
        
        return self._id
    
    @property
    def vec_id(self) -> Optional[UUID]:
        
        return self._vec_id
    
    @vec_id.setter
    def vec_id(self, new_vec_id: UUID) -> None:
        assert isinstance(new_vec_id, UUID)
        self._vec_id = new_vec_id
    
    @property
    def filepath(self) -> Path:
        
        return self._filepath
    
    @lazy_property
    def modification_time(self) -> float:
        
        return self._modification_time
    
    @classmethod
    def from_document(cls, document: dict) -> Self:
        
        # Create note instance
        note = cls(
            filepath=document["filepath"],
            modification_time=document["modification_time"]
        )
        
        # Set ID
        note._id = document["_id"]
        
        # Set vector ID
        note._vec_id = UUID(document["vec_id"])
        
        return note
        
    def to_document(self, with_id: bool = False) -> dict:
    
        # Convert to dict
        note = {
            "vec_id": self.vec_id.hex,
            "filepath": str(self.filepath),
            "modification_time": self.modification_time
        }
        
        # Set ID if required
        if with_id:
            note["id"] = self.id
            
        return note
