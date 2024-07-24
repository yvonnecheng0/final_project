from databases import get_user_id_by_username
from problems_leet import get_problems_by_user


user_id = get_user_id_by_username('wow13')
problems = get_problems_by_user(user_id)
print(get_problems_by_user(3))
