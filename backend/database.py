import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional
from bson import ObjectId
from datetime import datetime, timedelta
import os
from config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.create_indexes()
    
    def create_indexes(self):
        """Create necessary indexes for the collections"""
        try:
            # Users collection indexes
            self.db.users.create_index([("user_id", ASCENDING)], unique=True)
            self.db.users.create_index([("is_active", ASCENDING)])
            self.db.users.create_index([("gender", ASCENDING)])
            self.db.users.create_index([("city", ASCENDING)])
            self.db.users.create_index([("created_at", DESCENDING)])
            
            # Likes collection indexes
            self.db.likes.create_index([("user_id", ASCENDING), ("liked_user_id", ASCENDING)], unique=True)
            self.db.likes.create_index([("liked_user_id", ASCENDING)])
            self.db.likes.create_index([("created_at", DESCENDING)])
            
            # Messages collection indexes
            self.db.messages.create_index([("from_user_id", ASCENDING), ("to_user_id", ASCENDING)])
            self.db.messages.create_index([("to_user_id", ASCENDING)])
            self.db.messages.create_index([("created_at", DESCENDING)])
            
            # Blocks collection indexes
            self.db.blocks.create_index([("user_id", ASCENDING), ("blocked_user_id", ASCENDING)], unique=True)
            
            # Complaints collection indexes
            self.db.complaints.create_index([("user_id", ASCENDING)])
            self.db.complaints.create_index([("status", ASCENDING)])
            self.db.complaints.create_index([("created_at", DESCENDING)])
            
            # Payments collection indexes
            self.db.payments.create_index([("user_id", ASCENDING)])
            self.db.payments.create_index([("status", ASCENDING)])
            self.db.payments.create_index([("created_at", DESCENDING)])
            
            logger.info("✅ Created MongoDB indexes")
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    # User Methods
    def get_users(self, skip: int = 0, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
        """Get users with pagination and filtering"""
        try:
            query = filters or {}
            cursor = self.db.users.find(query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by user_id"""
        try:
            return self.db.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_users_count(self, filters: Optional[Dict] = None) -> int:
        """Get total users count"""
        try:
            query = filters or {}
            return self.db.users.count_documents(query)
        except Exception as e:
            logger.error(f"Error getting users count: {e}")
            return 0
    
    def update_user(self, user_id: int, update_data: Dict) -> bool:
        """Update user data"""
        try:
            result = self.db.users.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and all related data"""
        try:
            # Start a session for transaction
            with self.client.start_session() as session:
                with session.start_transaction():
                    # Delete user
                    self.db.users.delete_one({"user_id": user_id})
                    # Delete related data
                    self.db.likes.delete_many({"$or": [{"user_id": user_id}, {"liked_user_id": user_id}]})
                    self.db.messages.delete_many({"$or": [{"from_user_id": user_id}, {"to_user_id": user_id}]})
                    self.db.blocks.delete_many({"$or": [{"user_id": user_id}, {"blocked_user_id": user_id}]})
                    self.db.complaints.delete_many({"user_id": user_id})
                    self.db.payments.delete_many({"user_id": user_id})
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    # Payment Methods
    def get_payments(self, skip: int = 0, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
        """Get payments with pagination and filtering"""
        try:
            query = filters or {}
            cursor = self.db.payments.find(query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            payments = list(cursor)
            
            # Add user information to payments
            for payment in payments:
                user = self.get_user(payment["user_id"])
                if user:
                    payment["first_name"] = user.get("first_name")
                    payment["username"] = user.get("username")
            
            return payments
        except Exception as e:
            logger.error(f"Error getting payments: {e}")
            return []
    
    def get_payment(self, payment_id: str) -> Optional[Dict]:
        """Get payment by ID"""
        try:
            payment = self.db.payments.find_one({"_id": ObjectId(payment_id)})
            if payment:
                user = self.get_user(payment["user_id"])
                if user:
                    payment["first_name"] = user.get("first_name")
                    payment["username"] = user.get("username")
            return payment
        except Exception as e:
            logger.error(f"Error getting payment: {e}")
            return None
    
    def update_payment_status(self, payment_id: str, status: str, admin_id: int, notes: str = None) -> bool:
        """Update payment status"""
        try:
            result = self.db.payments.update_one(
                {"_id": ObjectId(payment_id)},
                {"$set": {
                    "status": status,
                    "processed_at": datetime.utcnow(),
                    "processed_by": admin_id,
                    "admin_notes": notes
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    def get_payments_count(self, filters: Optional[Dict] = None) -> int:
        """Get payments count"""
        try:
            query = filters or {}
            return self.db.payments.count_documents(query)
        except Exception as e:
            logger.error(f"Error getting payments count: {e}")
            return 0
    
    # Complaint Methods
    def get_complaints(self, skip: int = 0, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
        """Get complaints with pagination and filtering"""
        try:
            query = filters or {}
            cursor = self.db.complaints.find(query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error getting complaints: {e}")
            return []
    
    def update_complaint_status(self, complaint_id: str, status: str) -> bool:
        """Update complaint status"""
        try:
            result = self.db.complaints.update_one(
                {"_id": ObjectId(complaint_id)},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating complaint status: {e}")
            return False
    
    # Stats Methods
    def get_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get dashboard statistics for given date range"""
        try:
            # Date filter for queries
            date_filter = {}
            if start_date and end_date:
                date_filter = {"created_at": {"$gte": start_date, "$lte": end_date}}
            elif start_date:
                date_filter = {"created_at": {"$gte": start_date}}
            elif end_date:
                date_filter = {"created_at": {"$lte": end_date}}
            
            # Get current period stats
            total_users = self.db.users.count_documents({})
            active_users = self.db.users.count_documents({"is_active": True})
            
            # Calculate mutual matches (users who liked each other)
            likes = list(self.db.likes.find())
            user_likes = {}
            for like in likes:
                if like["user_id"] not in user_likes:
                    user_likes[like["user_id"]] = []
                user_likes[like["user_id"]].append(like["liked_user_id"])
            
            mutual_matches = 0
            for user_id, liked_users in user_likes.items():
                for liked_user_id in liked_users:
                    if liked_user_id in user_likes and user_id in user_likes[liked_user_id]:
                        mutual_matches += 1
            
            # Since each match is counted twice, divide by 2
            total_matches = mutual_matches // 2
            
            pending_payments = self.db.payments.count_documents({"status": "pending"})
            
            # Get previous period for growth calculation
            if start_date and end_date:
                period_days = (end_date - start_date).days
                prev_start_date = start_date - timedelta(days=period_days)
                prev_end_date = start_date
                
                prev_total_users = self.db.users.count_documents({
                    "created_at": {"$gte": prev_start_date, "$lte": prev_end_date}
                })
                prev_active_users = self.db.users.count_documents({
                    "is_active": True,
                    "created_at": {"$gte": prev_start_date, "$lte": prev_end_date}
                })
                
                # For matches and payments in previous period, we'd need more complex queries
                # For simplicity, using approximations
                prev_total_matches = max(total_matches - 50, 0)
                prev_pending_payments = max(pending_payments - 2, 0)
            else:
                # Default to last 30 days vs previous 30 days
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                prev_end_date = start_date
                prev_start_date = prev_end_date - timedelta(days=30)
                
                prev_total_users = self.db.users.count_documents({
                    "created_at": {"$gte": prev_start_date, "$lte": prev_end_date}
                })
                prev_active_users = self.db.users.count_documents({
                    "is_active": True,
                    "created_at": {"$gte": prev_start_date, "$lte": prev_end_date}
                })
                prev_total_matches = max(total_matches - 50, 0)
                prev_pending_payments = max(pending_payments - 2, 0)
            
            # Calculate growth percentages
            user_growth = self._calculate_growth(total_users, prev_total_users)
            active_growth = self._calculate_growth(active_users, prev_active_users)
            matches_growth = self._calculate_growth(total_matches, prev_total_matches)
            payments_growth = self._calculate_growth(pending_payments, prev_pending_payments)
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_matches": total_matches,
                "pending_payments": pending_payments,
                "user_growth": user_growth,
                "active_growth": active_growth,
                "matches_growth": matches_growth,
                "payments_growth": payments_growth
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def _calculate_growth(self, current: int, previous: int) -> float:
        """Calculate percentage growth"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
    
    # Chart Data Methods
    def get_gender_distribution(self) -> Dict[str, List]:
        """Get gender distribution data for charts"""
        try:
            pipeline = [
                {"$group": {"_id": "$gender", "count": {"$sum": 1}}},
                {"$project": {"gender": "$_id", "count": 1, "_id": 0}}
            ]
            result = list(self.db.users.aggregate(pipeline))
            
            labels = []
            data = []
            
            for item in result:
                gender = item["gender"] or "Not specified"
                labels.append(gender.capitalize())
                data.append(item["count"])
            
            return {"labels": labels, "data": data}
        except Exception as e:
            logger.error(f"Error getting gender distribution: {e}")
            return {"labels": [], "data": []}
    
    def get_registration_data(self, days: int = 7) -> Dict[str, List]:
        """Get user registration data for charts"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            pipeline = [
                {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            result = list(self.db.users.aggregate(pipeline))
            
            # Generate all dates in range
            dates = []
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            # Create count array with zeros
            counts = {item["_id"]: item["count"] for item in result}
            registration_counts = [counts.get(date, 0) for date in dates]
            
            # Format dates for display
            display_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d") for date in dates]
            
            return {"labels": display_dates, "data": registration_counts}
        except Exception as e:
            logger.error(f"Error getting registration data: {e}")
            return {"labels": [], "data": []}

# Global database instance
db = Database()