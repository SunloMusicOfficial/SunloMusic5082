import time
from collections import defaultdict

user_last_cmd = defaultdict(float)
COOLDOWN = 3.0 

def is_rate_limited(user_id: int) -> bool:
    now = time.time()
    if now - user_last_cmd[user_id] < COOLDOWN:
        return True
    user_last_cmd[user_id] = now
    return False
