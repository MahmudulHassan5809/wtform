from typing import Generic, Any, List, Optional, TypeVar, Dict, cast

from column import Column


T = TypeVar("T", bound="Table")


class Table(Generic[T]):
    def __init__(self, con=None):
        self.con = con
        self.columns = []
        self.model = None
        self.name = getattr(self.__class__, "__tablename__")
        self._initialize_columns()

    def _initialize_columns(self):
        """Dynamically initialize columns from the class definition."""
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, Column):
                self.columns.append(attr)

    def add_column(self, column: Column):
        self.columns.append(column)

    def create_table_sql(self) -> str:
        """Generate the SQL to create the table based on columns."""
        column_definitions = []
        for column in self.columns:
            col_def = f"{column.name} {column.data_type}"
            if column.primary_key:
                col_def += " PRIMARY KEY"
            if not column.nullable:
                col_def += " NOT NULL"
            if column.foreign_key:
                table, col = column.foreign_key.split(".")
                col_def += f" REFERENCES {table}({col})"
            column_definitions.append(col_def)
        columns_sql = ", ".join(column_definitions)
        return f"CREATE TABLE IF NOT EXISTS {self.name} ({columns_sql});"

    def insert(self, **fields: Any) -> T:
        """Insert data into the table and return the created record."""
        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())
        sql = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"
        cursor = self.con.execute(sql, values)

        # Assuming the database is auto-generating the ID, get the last inserted ID
        last_insert_id = cursor.lastrowid

        # Assuming that the object fields contain all the necessary attributes
        instance = self.__class__.__new__(
            self.__class__
        )  # Create instance of the subclass
        setattr(instance, "id", last_insert_id)
        for col_name, value in fields.items():
            setattr(instance, col_name, value)

        return cast(T, instance)

    def get(self, where: Dict[str, Any]) -> T | None:
        """Retrieve a single record from the table based on a WHERE condition."""
        condition = " AND ".join([f"{key} = ?" for key in where.keys()])
        query = f"SELECT * FROM {self.name} WHERE {condition} LIMIT 1"
        result = self.con.cursor.execute(query, list(where.values())).fetchone()

        if result:
            instance = self.__class__.__new__(
                self.__class__
            )  # Create instance of the subclass
            print(self.__class__, "---ss-")
            for i, col in enumerate(self.columns):
                setattr(instance, col.name, result[i])
            return cast(T, instance)
        return None

    def delete(self, where: Dict[str, Any]) -> int:
        """Delete a record from the table and return the number of affected rows."""
        condition = " AND ".join([f"{key} = ?" for key in where.keys()])
        query = f"DELETE FROM {self.name} WHERE {condition}"

        # Execute the delete query and get the number of affected rows
        cursor = self.con.execute(
            query, list(where.values())
        )  # You can return number of rows affected here

        return cursor.rowcount

    def update(self, where: Dict[str, Any], **fields: Any) -> T | None:
        """Update a record in the table and return the updated model object."""
        set_clause = ", ".join([f"{key} = ?" for key in fields.keys()])
        condition = " AND ".join([f"{key} = ?" for key in where.keys()])
        query = f"UPDATE {self.name} SET {set_clause} WHERE {condition}"
        values = list(fields.values()) + list(where.values())
        self.con.execute(query, values)
        updated_record = self.get(where)
        return updated_record

    def execute_query(
        self, query: str, params: Optional[list] = None
    ) -> List[Dict[str, Any]]:
        """Helper method to execute a query and fetch all results."""
        params = params or []
        cursor = self.con.cursor
        cursor.execute(query, params)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        return [dict(zip(column_names, row)) for row in results]

    def fetch_all(self) -> List[T]:
        """Fetch all rows from the table."""
        query = f"SELECT * FROM {self.name}"
        rows = self.execute_query(query)
        return [self._row_to_instance(row) for row in rows]

    def _build_filter_conditions(self, filters: Dict[str, Any]) -> tuple[list, list]:
        """
        Build SQL conditions and parameters for filters.
        """
        query_conditions = []
        params = []

        # Mapping of suffixes to SQL operators
        operator_map = {
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
            "exact": "=",
            "like": "LIKE",
        }

        for key, value in filters.items():
            if "__" in key:
                field, op = key.split("__", 1)
                sql_op = operator_map.get(op)
                if not sql_op:
                    raise ValueError(f"Unsupported filter operation: {op}")
                query_conditions.append(f"{field} {sql_op} ?")
            else:
                query_conditions.append(f"{key} = ?")
            params.append(value)

        return query_conditions, params

    def filter(self, **filters: Any) -> List[T]:
        """
        Fetch rows that match the given filters with support for advanced operations.
        """
        if not filters:
            raise ValueError("Filters cannot be empty.")

        query_conditions, params = self._build_filter_conditions(filters)
        where_clause = " AND ".join(query_conditions)
        query = f"SELECT * FROM {self.name} WHERE {where_clause}"
        rows = self.execute_query(query, params)
        return [self._row_to_instance(row) for row in rows]

    def paginate(self, page: int, per_page: int, **filters: Any) -> List[T]:
        """
        Fetch paginated rows from the table using filters with LIMIT and OFFSET.
        """
        if page < 1 or per_page < 1:
            raise ValueError("Page and per_page must be positive integers.")

        offset = (page - 1) * per_page

        # Build the WHERE clause using the filter logic
        query_conditions = []
        params = []
        if filters:
            query_conditions, params = self._build_filter_conditions(filters)
            where_clause = " WHERE " + " AND ".join(query_conditions)
        else:
            where_clause = ""

        # Add LIMIT and OFFSET to the query
        query = f"SELECT * FROM {self.name}{where_clause} LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        rows = self.execute_query(query, params)
        return [self._row_to_instance(row) for row in rows]

    def join(
        self,
        other_table: "Table",
        on_column: str,
        join_type: str = "INNER",
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> List[T]:
        """
        Perform a join operation between this table and another table with support for filters and pagination.
        Args:
            other_table: The Table instance to join with.
            on_column: The column name in the current table used for the join.
            join_type: The type of join operation ('INNER', 'LEFT', etc.).
            filters: A dictionary of filters to apply (optional).
            page: The page number for pagination (default is 1).
            per_page: The number of items per page (default is 10).
        Returns:
            A list of joined results as dictionaries or model instances.
        """
        # Identify the join column
        current_table_column = f"{self.name}.{on_column}"
        other_table_column = f"{other_table.name}.{on_column.split('_')[1]}"

        # Build the JOIN SQL query
        query = f"""
        SELECT {self.name}.*, {', '.join([f'{other_table.name}.{col.name} AS {other_table.name}_{col.name}' for col in other_table.columns])}
        FROM {self.name}
        {join_type.upper()} JOIN {other_table.name}
        ON {current_table_column} = {other_table_column}
        """

        # Add filters if provided
        if filters:
            query_conditions, params = self._build_filter_conditions(filters)
            where_clause = " AND ".join(query_conditions)
            query += f" WHERE {where_clause}"
        else:
            params = []

        # Add pagination
        offset = (page - 1) * per_page
        query += f" LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        # Execute the query
        rows = self.execute_query(query, params)

        result = []
        for row in rows:
            main_table_data = {
                key: value
                for key, value in row.items()
                if not key.startswith(other_table.name)
            }
            related_table_data = {
                key: value
                for key, value in row.items()
                if key.startswith(other_table.name)
            }

            # Create main table instance
            main_instance = self._row_to_instance(dict(main_table_data.items()))

            # Create related table instance
            related_instance = other_table._row_to_instance(
                {
                    key[len(other_table.name) + 1 :]: value
                    for key, value in related_table_data.items()
                }
            )

            # Attach the related instance to the main instance
            setattr(
                main_instance, other_table.name[:-1], related_instance
            )  # Remove 's' from 'users' to get 'user'

            result.append(main_instance)

        return result

    def _row_to_instance(self, row: Dict[str, Any]) -> T:
        """Convert a row dictionary to a model instance."""
        instance = self.__class__.__new__(
            self.__class__
        )  # Create an uninitialized instance
        for key, value in row.items():
            setattr(instance, key, value)
        return cast(T, instance)
