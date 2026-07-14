import uuid
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.models.models import NotificationModel
from app.models.schemas import NotificationResponse, NotificationItem

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, user_id: str) -> NotificationResponse:
        """
        Get all notifications for a specific user, sorted by timestamp descending.
        """
        notifications = self.db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id
        ).order_by(desc(NotificationModel.timestamp)).all()

        unread_count = self.db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False
        ).count()

        items = []
        for n in notifications:
            items.append(
                NotificationItem(
                    id=n.id,
                    message=n.message,
                    priority=n.priority,
                    is_read=n.is_read,
                    timestamp=n.timestamp.isoformat()
                )
            )

        return NotificationResponse(
            notifications=items,
            unread_count=unread_count
        )

    def mark_notifications_read(self, notification_ids: List[str]) -> int:
        """
        Mark specified notifications as read. Returns count of modified notifications.
        """
        updated = self.db.query(NotificationModel).filter(
            NotificationModel.id.in_(notification_ids)
        ).update({"is_read": True}, synchronize_session=False)
        self.db.commit()
        return updated

    def send_notification(self, user_id: str, message: str, priority: str = "info") -> NotificationModel:
        """
        Helper method to insert a new notification.
        """
        notif = NotificationModel(
            id=f"notif_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            message=message,
            priority=priority,
            is_read=False,
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif
