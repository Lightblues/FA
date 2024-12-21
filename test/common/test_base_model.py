from pydantic import BaseModel
from typing import Optional

# class CustomModel(BaseModel):
#     def model_dump(self, **kwargs):
#         # Use dict comprehension to filter out None values
#         return {k: v for k, v in super().model_dump(**kwargs).items() if v is not None}


class Person(BaseModel):
    name: str
    age: Optional[int] = None
    email: Optional[str] = None


person = Person(name="Alice", age=None, email=None)
print(person.model_dump())  # Output: {'name': 'Alice'}
print(person.model_dump(exclude_none=True))  # Output: {'name': 'Alice'}
print()
