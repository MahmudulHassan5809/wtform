```
# 🐍 SimpleORM - A Lightweight SQLite ORM-Like Layer

> ⚠️ **Disclaimer**: This project is for educational and experimental purposes only.
> **Do NOT use this in real-world or production applications.**
> It lacks proper security, robustness, migrations, and validation you'd expect from a full ORM.

---

## 🚀 Features

- Define tables with columns using Python classes.
- Automatically generates `CREATE TABLE` SQL from class definitions.
- Supports basic CRUD operations (`insert`, `get`, `update`, `delete`).
- Filter records with flexible syntax (`exact`, `like`, `gt`, `lt`, etc.).
- Pagination and join support.
- Easy-to-use database connection manager.

---

## 📁 Project Structure

```

simpleorm/
├── column.py # Column definition for table schemas
├── database.py # Database connection manager and logic
├── table.py # Base Table class with ORM-like methods
├── models/
│ ├── user.py # Example User model
│ └── post.py # Example Post model
├── main.py # Example usage

````

---

## 🧱 Defining a Table

Tables are defined by subclassing `Table` and adding `Column` fields as class attributes.

```python
# models/user.py

from column import Column
from table import Table

class User(Table["User"]):
    __tablename__ = "users"

    id = Column("id", "INTEGER", primary_key=True, nullable=False)
    name = Column("name", "TEXT", nullable=False)
    email = Column("email", "TEXT", nullable=False)
    age = Column("age", "INTEGER")
````

```python
# models/post.py

from column import Column
from table import Table

class Post(Table["Post"]):
    __tablename__ = "posts"

    id = Column("id", "INTEGER", primary_key=True, nullable=False)
    user_id = Column("user_id", "INTEGER", nullable=False, foreign_key="users.id")
    title = Column("title", "TEXT", nullable=False)
    description = Column("description", "TEXT")
```

---

## ⚙️ Setting Up the Database

```python
# main.py

from database import Database
from models.user import User
from models.post import Post

with Database("app.db").get_conn() as db:
    db.create_all([User(db), Post(db)])
```

---

## 📝 Basic CRUD Usage

### Insert

```python
user_table = User(db)
new_user = user_table.insert(name="Alice", email="alice@example.com", age=30)
```

### Get

```python
user = user_table.get({"email": "alice@example.com"})
```

### Update

```python
updated_user = user_table.update({"email": "alice@example.com"}, age=31)
```

### Delete

```python
deleted_count = user_table.delete({"id": new_user.id})
```

---

## 🔍 Filtering Records

```python
# Exact match
users = user_table.filter(name="Alice")

# LIKE query
users = user_table.filter(name__like="%lic%")

# Greater than / Less than
users = user_table.filter(age__gt=25)
```

---

## 📄 Pagination

```python
users = user_table.paginate(page=2, per_page=5)
```

---

## 🔗 Join Tables

```python
post_table = Post(db)
results = post_table.join(
    other_table=User(db),
    on_column="user_id",
    filters={"users.age__gte": 25},
    page=1,
    per_page=10
)
```

---

## 🧪 Example Output

```python
print(results[0].title)
print(results[0].user.name)  # Manually set via post.user = user if needed
```

---

## 🛠️ Design Philosophy

- Keep it **simple** and **explicit**.
- No magic metaclasses or background threading.
- Easy to read and modify for learning or small projects.
- Encourage understanding of SQL and Python internals.

---

## 📌 Requirements

- Python 3.10+
- Standard Library only (no external dependencies)

---

## 📜 License

This project is open source and free to use under the MIT License.

---

## 💡 Future Ideas

- Support for migrations
- Relationship resolution (e.g., auto `.user` population)
- More SQL dialect support
- Async support via `aiosqlite`

---

## 👏 Contributing

Just having fun? Great! Want to contribute? Feel free to fork and submit a PR!

---
