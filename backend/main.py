from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from models import (
    User, UserResponse, PaymentResponse, StatsResponse, 
    ChartDataResponse, DateRangeRequest, PaymentUpdateRequest,
    LoginRequest, Token
)
from database import db
from auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dating Bot Admin API",
    description="Backend API for Dating Bot Admin Dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/dashboard/stats", response_model=StatsResponse)
async def get_dashboard_stats(
    range_type: str = Query("last7", description="Date range type"),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics for the given date range"""
    try:
        end_date = datetime.utcnow()
        
        if range_type == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif range_type == "yesterday":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end_date = start_date + timedelta(days=1)
        elif range_type == "last7":
            start_date = end_date - timedelta(days=7)
        elif range_type == "last30":
            start_date = end_date - timedelta(days=30)
        elif range_type == "last90":
            start_date = end_date - timedelta(days=90)
        elif range_type == "thisMonth":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif range_type == "lastMonth":
            start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = start_date.replace(day=28) + timedelta(days=4)  # Last day of month
        elif range_type == "thisYear":
            start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date - timedelta(days=7)  # Default to last 7 days
        
        stats = db.get_stats(start_date, end_date)
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/charts/gender-distribution", response_model=ChartDataResponse)
async def get_gender_distribution(current_user: dict = Depends(get_current_user)):
    """Get gender distribution data for charts"""
    try:
        data = db.get_gender_distribution()
        return ChartDataResponse(**data)
    except Exception as e:
        logger.error(f"Error getting gender distribution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/charts/registrations")
async def get_registration_data(
    days: int = Query(7, description="Number of days to show"),
    current_user: dict = Depends(get_current_user)
):
    """Get user registration data for charts"""
    try:
        data = db.get_registration_data(days)
        return ChartDataResponse(**data)
    except Exception as e:
        logger.error(f"Error getting registration data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Users endpoints
@app.get("/users", response_model=List[dict])
async def get_users(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: dict = Depends(get_current_user)
):
    """Get users with pagination and search"""
    try:
        filters = {}
        if search:
            filters["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}}
            ]
        
        users = db.get_users(skip, limit, filters)
        # Convert ObjectId to string for JSON serialization
        for user in users:
            user["_id"] = str(user["_id"])
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get user by ID"""
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/users/{user_id}")
async def update_user(
    user_id: int, 
    update_data: dict, 
    current_user: dict = Depends(get_current_user)
):
    """Update user data"""
    try:
        success = db.update_user(user_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
        return {"message": "User updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Delete user and all related data"""
    try:
        success = db.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Payments endpoints
@app.get("/payments", response_model=List[dict])
async def get_payments(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """Get payments with pagination and filtering"""
    try:
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        
        payments = db.get_payments(skip, limit, filters)
        # Convert ObjectId to string for JSON serialization
        for payment in payments:
            payment["_id"] = str(payment["_id"])
        return payments
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/payments/{payment_id}", response_model=dict)
async def get_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    """Get payment by ID"""
    try:
        payment = db.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        payment["_id"] = str(payment["_id"])
        return payment
    except Exception as e:
        logger.error(f"Error getting payment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/payments/{payment_id}")
async def update_payment_status(
    payment_id: str,
    update_data: PaymentUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update payment status"""
    try:
        # In a real app, you'd get the admin ID from the token
        admin_id = 1  # Default admin ID
        
        success = db.update_payment_status(
            payment_id, 
            update_data.status, 
            admin_id, 
            update_data.admin_notes
        )
        if not success:
            raise HTTPException(status_code=404, detail="Payment not found or no changes made")
        return {"message": "Payment status updated successfully"}
    except Exception as e:
        logger.error(f"Error updating payment status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Complaints endpoints
@app.get("/complaints", response_model=List[dict])
async def get_complaints(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """Get complaints with pagination and filtering"""
    try:
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        
        complaints = db.get_complaints(skip, limit, filters)
        # Convert ObjectId to string for JSON serialization
        for complaint in complaints:
            complaint["_id"] = str(complaint["_id"])
        return complaints
    except Exception as e:
        logger.error(f"Error getting complaints: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/complaints/{complaint_id}")
async def update_complaint_status(
    complaint_id: str,
    status: str = Query(..., description="New status for complaint"),
    current_user: dict = Depends(get_current_user)
):
    """Update complaint status"""
    try:
        success = db.update_complaint_status(complaint_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Complaint not found or no changes made")
        return {"message": "Complaint status updated successfully"}
    except Exception as e:
        logger.error(f"Error updating complaint status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)