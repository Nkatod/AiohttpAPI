from sqlalchemy.sql.expression import text

t = text("SELECT * FROM users WHERE id=:user_id")
result = connection.execute(t, user_id=12)