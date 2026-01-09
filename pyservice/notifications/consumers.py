"""
WebSocket Consumers
PyService Mini-ITSM Platform

Real-time notification consumers using Django Channels.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Each user connects to their own notification channel.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Create a unique group for the user
        self.user_group = f'notifications_{self.user.pk}'
        
        # Join the user's notification group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial unread count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'init',
            'unread_count': unread_count,
            'message': 'Connected to notification stream'
        }))
        
        logger.info(f"User {self.user.username} connected to notifications")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
            logger.info(f"User {self.user.username} disconnected from notifications")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'mark_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)
                await self.send(text_data=json.dumps({
                    'type': 'notification_read',
                    'notification_id': notification_id
                }))
            
            elif action == 'mark_all_read':
                await self.mark_all_read()
                await self.send(text_data=json.dumps({
                    'type': 'all_read',
                    'message': 'All notifications marked as read'
                }))
            
            elif action == 'get_unread':
                unread_count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': unread_count
                }))
            
            elif action == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def notification_message(self, event):
        """
        Handle notification messages from the channel layer.
        Called when a notification is broadcast to the user's group.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
            'unread_count': await self.get_unread_count()
        }))
    
    async def sla_alert(self, event):
        """Handle SLA alert messages."""
        await self.send(text_data=json.dumps({
            'type': 'sla_alert',
            'alert': event['alert'],
            'severity': event.get('severity', 'warning')
        }))
    
    async def system_message(self, event):
        """Handle system-wide messages."""
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for the user."""
        from notifications.models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read."""
        from notifications.models import Notification
        Notification.objects.filter(
            pk=notification_id,
            user=self.user
        ).update(is_read=True)
    
    @database_sync_to_async
    def mark_all_read(self):
        """Mark all notifications as read."""
        from notifications.models import Notification
        Notification.objects.filter(
            user=self.user,
            is_read=False
        ).update(is_read=True)


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time dashboard updates.
    Broadcasts metrics updates to all connected users.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Join the dashboard group
        self.dashboard_group = 'dashboard_updates'
        
        await self.channel_layer.group_add(
            self.dashboard_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial metrics
        metrics = await self.get_dashboard_metrics()
        await self.send(text_data=json.dumps({
            'type': 'init',
            'metrics': metrics
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'dashboard_group'):
            await self.channel_layer.group_discard(
                self.dashboard_group,
                self.channel_name
            )
    
    async def metrics_update(self, event):
        """Handle metrics update messages."""
        await self.send(text_data=json.dumps({
            'type': 'metrics_update',
            'metrics': event['metrics']
        }))
    
    async def incident_update(self, event):
        """Handle incident update messages."""
        await self.send(text_data=json.dumps({
            'type': 'incident_update',
            'incident': event['incident'],
            'action': event.get('action', 'update')
        }))
    
    @database_sync_to_async
    def get_dashboard_metrics(self):
        """Get current dashboard metrics."""
        from incidents.models import Incident
        from service_requests.models import ServiceRequest
        
        return {
            'open_incidents': Incident.objects.exclude(
                state__in=['resolved', 'closed']
            ).count(),
            'pending_requests': ServiceRequest.objects.filter(
                state='awaiting_approval'
            ).count(),
            'sla_at_risk': Incident.objects.filter(
                state__in=['new', 'in_progress'],
                sla_breached=False
            ).count(),
        }


# Helper function to send notifications
async def send_notification_to_user(user_id, notification_data):
    """
    Send a real-time notification to a specific user.
    Call this from anywhere in the application to push notifications.
    """
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'notifications_{user_id}',
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )


async def broadcast_dashboard_update(metrics):
    """Broadcast dashboard metrics update to all connected users."""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'dashboard_updates',
        {
            'type': 'metrics_update',
            'metrics': metrics
        }
    )
