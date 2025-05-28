
from column import Column
from table import Table


class User(Table["User"]):
    __tablename__ = "users"

    # Define columns as class attributes
    id = Column(name="id", data_type="INTEGER", primary_key=True, nullable=False)
    name = Column(name="name", data_type="TEXT", nullable=False)
    email = Column(name="email", data_type="TEXT", nullable=False)
    age = Column(name="age", data_type="INTEGER", nullable=True)


class Post(Table["Post"]):
    __tablename__ = "posts"

    id = Column(name="id", data_type="INTEGER", primary_key=True, nullable=False)
    user_id = Column(
        name="user_id", data_type="INTEGER", nullable=False, foreign_key="users.id"
    )
    title = Column(name="title", data_type="TEXT", nullable=False)
    description = Column(name="description", data_type="TEXT", nullable=True)

    @property
    def user(self) -> "User":
        return self.__user  # No checks here

    @user.setter
    def user(self, value: "User") -> None:
        self.__user = value  # Accept any value
