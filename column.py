# column.py


class Column:
    def __init__(
        self,
        name: str,
        data_type: str,
        primary_key: bool = False,
        nullable: bool = True,
        foreign_key: str | None = None,
    ):
        """
        Represents a column in a database table.

        Args:
            name (str): Name of the column.
            data_type (str): SQL data type of the column.
            primary_key (bool): Whether the column is a primary key.
            nullable (bool): Whether the column allows NULL values.
            foreign_key (str): Foreign key reference in the format "TableName(ColumnName)".
        """
        self.name = name
        self.data_type = data_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.foreign_key = foreign_key

    def __repr__(self):
        return f"Column(name={self.name}, type={self.data_type}, primary_key={self.primary_key}, nullable={self.nullable}, foreign_key={self.foreign_key})"
