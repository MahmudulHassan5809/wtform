# main.py

from database import Database
from model import User, Post
from utils import model_to_table

# Define the database once
db = Database("my_database.db")

if __name__ == "__main__":
    with db.get_conn() as con:
        # Create tables from models
        user_table = model_to_table(User, con)
        post_table = model_to_table(Post, con)

        # Create tables in the database
        con.create_all([user_table, post_table])

        # Insert test data
        for i in range(1, 101):
            user_table.insert(id=i, name=f"User {i}", email=f"user{i}@example.com", age=20 + i)

        # # Paginated fetch with filters
        # page1 = user_table.paginate(page=1, per_page=10, age__gte=30)
        # print("Page 1 (age >= 30):", page1)

        # page2 = user_table.paginate(page=2, per_page=10, age__gte=30)
        # print("Page 2 (age >= 30):", page2)

        # user = user_table.insert(
        #     **{"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30}
        # )
        # post = post_table.insert(
        #     id=1, title="My First Post", description="Test", user_id=user.id
        # )

        # posts_with_users = post_table.join(
        #     user_table,
        #     on_column="user_id",
        #     join_type="INNER",
        #     filters={"title": "XXX"},
        # )
        # for post in posts_with_users:
        #     print(
        #         f"Post Title: {post.title}, Author: {post.user.name}, Email: {post.user.email}"
        #     )

        # user_table.get(where={"id": 1})
        # user_table.update(where={"id": 1}, age=32)
        # user_table.delete(where={"id": 3})

        # users = user_table.fetch_all()
        # for user in users:
        #     print(f"User Found: Name: {user.name}, Email: {user.email}")

        # filtered_users = user_table.filter(name="John Doe", age__gte=30)
        # for user in filtered_users:
        #     print(f"User Found: Name: {user.name}, Email: {user.email}")

        # paginated_users = user_table.paginate(page=1, per_page=1)
        # for user in paginated_users:
        #     print(f"User Found: Name: {user.name}, Email: {user.email}")
