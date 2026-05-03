import os

# Tùy chỉnh quyền sử dụng các lệnh tại đây:
# - "everyone": Ai cũng dùng được
# - "owner": Chỉ người có OWNER_ID (trong file .env) mới dùng được
COMMAND_PERMISSIONS = {
    "join": "owner",
    "leave": "owner",
    "restart": "owner"
}

def check_permission(command_name: str, user_id: int) -> bool:
    """Kiểm tra xem user_id có quyền chạy lệnh command_name không"""
    perm = COMMAND_PERMISSIONS.get(command_name, "everyone")
    if perm == "owner":
        owner_id = int(os.getenv('OWNER_ID', 0))
        return user_id == owner_id
    return True
