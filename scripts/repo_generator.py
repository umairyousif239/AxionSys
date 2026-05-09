import os

BASE = "data/repo/synthetic_repo"

os.makedirs(BASE, exist_ok=True)

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def make_file(lines):
    return "\n".join(lines)

# -------------------------
# Core system modules
# -------------------------

db_layer = make_file([
    "class Database:",
    "    def __init__(self):",
    "        self.users = {}",
    "        self.cache = None  # BUG SOURCE",
    "",
    "    def get_user(self, email):",
    "        return self.users.get(email)",
])

cache_layer = make_file([
    "class Cache:",
    "    def __init__(self):",
    "        self.store = None",
    "",
    "    def get(self, key):",
    "        return self.store.get(key)",  # BUG: store is None
])

repo_layer = make_file([
    "from cache import Cache",
    "",
    "class UsersRepo:",
    "    def __init__(self, db, cache):",
    "        self.db = db",
    "        self.cache = cache",
    "",
    "    async def get_user(self, email):",
    "        cached = self.cache.get(email)",
    "        if cached:",
    "            return cached",
    "        return self.db.get_user(email)",
])

auth_layer = make_file([
    "from users_repo import UsersRepo",
    "",
    "class AuthService:",
    "    def __init__(self, repo):",
    "        self.repo = repo",
    "",
    "    async def authenticate(self, email):",
    "        user = await self.repo.get_user(email)",
    "        if not user:",
    "            raise Exception('Invalid user')",
    "        return user",
])

api_layer = make_file([
    "from auth import AuthService",
    "",
    "class API:",
    "    def __init__(self, auth):",
    "        self.auth = auth",
    "",
    "    async def login(self, email):",
    "        return await self.auth.authenticate(email)",
])

# -------------------------
# Write core files
# -------------------------

write(f"{BASE}/db.py", db_layer)
write(f"{BASE}/cache.py", cache_layer)
write(f"{BASE}/users_repo.py", repo_layer)
write(f"{BASE}/auth.py", auth_layer)
write(f"{BASE}/api.py", api_layer)

# -------------------------
# Inflate to ~1000 chunks
# -------------------------

for i in range(200):
    content = make_file([
        f"# module_{i}",
        "def helper():",
        "    data = {}",
        "    for j in range(50):",
        "        data[j] = j * i",
        "    return data",
    ])
    write(f"{BASE}/utils/module_{i}.py", content)

print(f"Repo generated at: {BASE}")