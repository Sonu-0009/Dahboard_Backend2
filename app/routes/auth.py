from fastapi import APIRouter, HTTPException, Request
from app.config.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------- Signup (only for users)
@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    db = get_db()
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.dict()
    user_dict["role"] = "user"   # default role
    result = db.users.insert_one(user_dict)

    return UserResponse(
        id=str(result.inserted_id),
        email=user.email,
        mobile=user.mobile,
        gender=user.gender,
        role="user"
    )


# ---------- Login
@router.post("/login")
async def login(user: UserLogin, request: Request):
    db = get_db()
    db_user = db.users.find_one({"email": user.email})

    if not db_user or db_user["password"] != user.password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Save session
    request.session["user_id"] = str(db_user["_id"])
    request.session["role"] = db_user["role"]
    
    request.session["email"] = db_user["email"]         # ✅ added

    # Redirect based on role
    if db_user["role"] == "super_admin":
        redirect_url = "/dashboard/super-admin"
    elif db_user["role"] == "admin":
        redirect_url = "/dashboard/admin"
    else:
        redirect_url = "/dashboard/user"

    return {
        "id": str(db_user["_id"]),
        "email": db_user["email"],
        "role": db_user["role"],
        "redirect_url": redirect_url
    }

# ---------- Create Admin (only by super_admin)
@router.post("/create-admin", response_model=UserResponse)
async def create_admin(new_admin: UserCreate, request: Request):
    if request.session.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Super Admin only")

    db = get_db()
    if db.users.find_one({"email": new_admin.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    admin_dict = new_admin.dict()
    admin_dict["role"] = "admin"
    result = db.users.insert_one(admin_dict)

    return UserResponse(
        id=str(result.inserted_id),
        username=new_admin.username,
        email=new_admin.email,
        mobile=new_admin.mobile,
        gender=new_admin.gender,
        role="admin"
    )


# ---------- Logout
@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}