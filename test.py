<<<<<<< HEAD
from sqlalchemy.sql.expression import text

t = text("SELECT * FROM users WHERE id=:user_id")
=======
from sqlalchemy.sql.expression import text

t = text("SELECT * FROM users WHERE id=:user_id")
>>>>>>> 4b0356d9b8929b4372a010fce368bc581a064d8f
result = connection.execute(t, user_id=12)