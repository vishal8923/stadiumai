import uuid
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import NotificationModel
from app.models.schemas import NotificationResponse, NotificationItem

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, user_id: str) -> NotificationResponse:
        notifications = self.db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
        ).order_by(desc(NotificationModel.timestamp)).all()

        unread_count = self.db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read.is_(False),
        ).count()

        items = [
            NotificationItem(
                id=n.id,
                message=n.message,
                priority=n.priority,
                is_read=n.is_read,
                timestamp=n.timestamp.isoformat(),
            )
            for n in notifications
        ]

        return NotificationResponse(
            notifications=items,
            unread_count=unread_count,
        )

    def mark_notifications_read(self, notification_ids: list[str]) -> int:
        updated = self.db.query(NotificationModel).filter(
            NotificationModel.id.in_(notification_ids),
        ).update({"is_read": True}, synchronize_session=False)
        self.db.commit()
        return updated

    def send_notification(self, user_id: str, message: str, priority: str = "info") -> NotificationModel:
        notif = NotificationModel(
            id=f"notif_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            message=message,
            priority=priority,
            is_read=False,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def send_notifications_batch(self, notifications: list[dict]) -> int:
        batch = [
            NotificationModel(
                id=f"notif_{uuid.uuid4().hex[:8]}",
                user_id=n["user_id"],
                message=n["message"],
                priority=n.get("priority", "info"),
                is_read=False,
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            for n in notifications
        ]
        if not batch:
            return 0
        self.db.add_all(batch)
        self.db.commit()
        return len(batch)
