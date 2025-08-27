from fastapi import APIRouter, HTTPException, Request
from app.config.database import get_db

router = APIRouter(prefix="/protected", tags=["Protected"])

# Helper function
def require_role(request: Request, role: str):
    user_role = request.session.get("role")
    if user_role != role:
        raise HTTPException(status_code=403, detail=f"{role} role required")

# Example: Super Admin only
@router.get("/super-admin-data")
async def super_admin_data(request: Request):
    require_role(request, "super_admin")
    return {"message": "Confidential data for Super Admin"}

# Example: Admin only
@router.get("/admin-stats")
async def admin_stats(request: Request):
    require_role(request, "admin")
    return {"message": "Admin stats data"}

# Example: User only
@router.get("/user-profile")
async def user_profile(request: Request):
    require_role(request, "user")
    return {
        "username": request.session.get("username"),
        "email": request.session.get("email"),
        "role": request.session.get("role")
    }

# ✅ NEW: Super Admin can view all users
@router.get("/all-users")
async def get_all_users(request: Request):
    require_role(request, "super_admin")   # only super admin allowed
    db = get_db()
    users = list(db.users.find({}, {"password": 0}))  # exclude password
    return {"users": [{**u, "_id": str(u["_id"])} for u in users]}