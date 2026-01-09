"""
Remote Support URLs
PyService Mini-ITSM Platform
"""

from django.urls import path
from . import views


urlpatterns = [
    # User endpoints
    path('request/', views.request_support, name='request_support'),
    path('my-sessions/', views.my_sessions, name='my_support_sessions'),
    
    # IT Staff endpoints
    path('queue/', views.support_queue, name='support_queue'),
    path('accept/<str:session_code>/', views.accept_session, name='accept_session'),
    
    # Session room
    path('session/<str:session_code>/', views.session_room, name='remote_session_room'),
    path('session/<str:session_code>/send/', views.send_message, name='session_send_message'),
    path('session/<str:session_code>/messages/', views.get_messages, name='session_get_messages'),
    path('session/<str:session_code>/complete/', views.complete_session, name='complete_session'),
    path('session/<str:session_code>/cancel/', views.cancel_session, name='cancel_session'),
    path('session/<str:session_code>/escalate/', views.escalate_session, name='escalate_session'),
    
    # Voice features
    path('session/<str:session_code>/voice/toggle/', views.toggle_voice, name='toggle_voice'),
    path('session/<str:session_code>/transcript/save/', views.save_transcript, name='save_transcript'),
    path('session/<str:session_code>/transcript/get/', views.get_full_transcript, name='get_full_transcript'),
]
