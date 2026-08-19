ROOT_ROLE_NAME = "Root"
SYSTEM_ROLE_NAME = "System"
ADMIN_ROLE_NAME = "Admin"
APP_USER_ROLE_NAME = "AppUser"

# Root and Admin can see/manage other users (GET /user/all, POST /user/info).
USER_MANAGEMENT_ROLE_NAMES = {ROOT_ROLE_NAME, ADMIN_ROLE_NAME}
