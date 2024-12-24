from pydantic import BaseModel, Field


class CustomRole(BaseModel):
    id: int = -1  # use negative id to distinguish built-in roles
    rolename: str
    prefix: str = Field(default="")
    color: str = Field(default="blue")

    def model_post_init(self, __context):
        if not self.prefix:  # set prefix only when it is empty
            self.prefix = f"[{self.rolename.upper()}] "
        self.rolename = self.rolename.lower()

    def __str__(self):
        return f"Role(id={self.id}, prefix={self.prefix}, name={self.rolename})"


class Role:
    """
    NOTE:
    - to use requests/pydantic, do not set Role as Enum
    """

    SYSTEM = CustomRole(id=0, rolename="system", prefix="[SYSTEM] ", color="green")
    USER = CustomRole(id=1, rolename="user", prefix="[USER] ", color="red")
    BOT = CustomRole(id=2, rolename="bot", prefix="[BOT] ", color="orange")

    @classmethod
    def get_by_rolename(cls, rolename: str) -> CustomRole:
        rolename = rolename.upper()
        if hasattr(cls, rolename):
            return getattr(cls, rolename)
        return CustomRole(rolename=rolename)
