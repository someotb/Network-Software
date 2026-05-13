import grpc
from concurrent import futures
import redis
import json
import logging
import os
import time
from datetime import datetime
import uuid

import notifications_pb2
import notifications_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class NotificationServiceServicer(notifications_pb2_grpc.NotificationServiceServicer):

    def SendNotification(self, request, context):
        try:
            notification_id = str(uuid.uuid4())

            notification_data = {
                "id": notification_id,
                "user_id": request.user_id,
                "type": request.type,
                "title": request.title,
                "message": request.message,
                "created_at": datetime.utcnow().isoformat(),
                "read": False
            }

            redis_key = f"notifications:user:{request.user_id}"
            redis_client.lpush(redis_key, json.dumps(notification_data))
            redis_client.ltrim(redis_key, 0, 99)

            logger.info(f"Notification sent to user {request.user_id}: {request.title}")

            return notifications_pb2.NotificationResponse(
                success=True,
                notification_id=notification_id,
                message="Notification sent successfully"
            )

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return notifications_pb2.NotificationResponse(
                success=False,
                notification_id="",
                message=f"Error: {str(e)}"
            )

    def GetNotifications(self, request, context):
        try:
            redis_key = f"notifications:user:{request.user_id}"
            limit = request.limit if request.limit > 0 else 10

            notifications_json = redis_client.lrange(redis_key, 0, limit - 1)

            for notif_json in notifications_json:
                notif_data = json.loads(notif_json)

                notification = notifications_pb2.Notification(
                    id=notif_data["id"],
                    user_id=notif_data["user_id"],
                    type=notif_data["type"],
                    title=notif_data["title"],
                    message=notif_data["message"],
                    created_at=notif_data["created_at"],
                    read=notif_data["read"]
                )

                yield notification

        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notifications_pb2_grpc.add_NotificationServiceServicer_to_server(
        NotificationServiceServicer(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()

    logger.info("Notification Service started on port 50051")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.stop(0)


if __name__ == '__main__':
    serve()
