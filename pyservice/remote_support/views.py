"""
Remote Support Views
PyService Mini-ITSM Platform

Views for remote support session management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import RemoteSupportSession, SessionMessage, VoiceTranscript

def is_support_staff(user):
    """Check if user is IT support staff."""
    if user.role == 'admin':
        return True
    if user.department:
        return user.department.code in ['IT_DEPARTMENT', 'SERVICENOW_SUPPORT']
    return False


@login_required
def request_support(request):
    """Create a new remote support request."""
    # IT staff should go to queue instead of request form
    if is_support_staff(request.user):
        return redirect('support_queue')
    
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        anydesk_id = request.POST.get('anydesk_id', '').strip()
        initial_message = request.POST.get('initial_message', '').strip()
        
        if subject and description and anydesk_id:
            session = RemoteSupportSession.objects.create(
                requester=request.user,
                subject=subject,
                description=description,
                priority=priority,
                anydesk_id=anydesk_id
            )
            # Create initial message if provided
            if initial_message:
                SessionMessage.objects.create(
                    session=session,
                    sender=request.user,
                    message=initial_message
                )
            messages.success(request, 'Support request created! Waiting for a technician to connect.')
            return redirect('remote_session_room', session_code=session.session_code)
        else:
            messages.error(request, 'Please fill in all required fields including AnyDesk ID.')
    
    return render(request, 'remote_support/request_form.html')


@login_required
def support_queue(request):
    """View pending support requests (IT staff only)."""
    if not is_support_staff(request.user):
        messages.error(request, 'Access denied. IT staff only.')
        return redirect('dashboard')
    
    pending = RemoteSupportSession.objects.filter(status='pending').order_by('-priority', 'created_at')
    active = RemoteSupportSession.objects.filter(
        status__in=['accepted', 'in_progress'],
        technician=request.user
    )
    
    if request.user.role == 'admin':
        completed = RemoteSupportSession.objects.filter(status='completed').order_by('-completed_at')[:50]
    else:
        # Non-admin staff only see their own completed sessions
        completed = RemoteSupportSession.objects.filter(
            status='completed', 
            technician=request.user
        ).order_by('-completed_at')[:50]
    
    return render(request, 'remote_support/queue.html', {
        'pending_sessions': pending,
        'active_sessions': active,
        'completed_sessions': completed,
    })


@login_required
@require_POST
def accept_session(request, session_code):
    """Accept a pending support session."""
    if not is_support_staff(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    if session.accept(request.user):
        messages.success(request, f'Session {session_code} accepted!')
        return redirect('remote_session_room', session_code=session_code)
    else:
        messages.error(request, 'Could not accept this session.')
        return redirect('support_queue')


@login_required
def session_room(request, session_code):
    """The support session room with chat."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Check access: only requester, technician, or admin can view
    if request.user != session.requester and request.user != session.technician:
        if not is_support_staff(request.user):
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get chat messages
    chat_messages = session.messages.all()
    
    # Determine user role in session
    is_technician = request.user == session.technician or is_support_staff(request.user)
    
    return render(request, 'remote_support/session_room.html', {
        'session': session,
        'chat_messages': chat_messages,
        'is_technician': is_technician,
    })


@login_required
@require_POST
def send_message(request, session_code):
    """Send a chat message in the session."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Check access
    if request.user != session.requester and request.user != session.technician:
        if not is_support_staff(request.user):
            return JsonResponse({'error': 'Access denied'}, status=403)
    
    message_text = request.POST.get('message', '').strip()
    if message_text:
        msg = SessionMessage.objects.create(
            session=session,
            sender=request.user,
            message=message_text
        )
        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'sender': msg.sender.get_full_name() or msg.sender.username,
                'message': msg.message,
                'time': msg.created_at.strftime('%H:%M'),
                'is_self': True,
            }
        })
    return JsonResponse({'error': 'Empty message'}, status=400)


@login_required
def get_messages(request, session_code):
    """Get new messages for the session (AJAX polling)."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    last_id = int(request.GET.get('last_id', 0))
    
    new_messages = session.messages.filter(id__gt=last_id)
    
    return JsonResponse({
        'messages': [
            {
                'id': msg.id,
                'sender': msg.sender.get_full_name() or msg.sender.username,
                'message': msg.message,
                'time': msg.created_at.strftime('%H:%M'),
                'is_self': msg.sender == request.user,
            }
            for msg in new_messages
        ],
        'session_status': session.status,
        'is_voice_active': session.is_voice_active,
    })



@login_required
@require_POST
def complete_session(request, session_code):
    """Complete the support session."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    if request.user != session.technician and not is_support_staff(request.user):
        messages.error(request, 'Only the technician can complete this session.')
        return redirect('remote_session_room', session_code=session_code)
    
    notes = request.POST.get('notes', '')
    if session.complete(notes):
        messages.success(request, 'Session completed successfully!')
    else:
        messages.error(request, 'Could not complete this session.')
    
    return redirect('support_queue')


@login_required
@require_POST
def cancel_session(request, session_code):
    """Cancel a support session."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Requester or technician can cancel
    if request.user not in [session.requester, session.technician]:
        if not is_support_staff(request.user):
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    if session.cancel():
        messages.info(request, 'Session cancelled.')
    else:
        messages.error(request, 'Could not cancel this session.')
    
    return redirect('my_support_sessions')


@login_required
@require_POST
def escalate_session(request, session_code):
    """Escalate a session to urgent and return to queue."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Only technician (or admin) can escalate
    if request.user != session.technician and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('remote_session_room', session_code=session_code)
    
    # Logic: Reset technician, Set pending, Set urgent, Add tag to subject
    if session.status in ['accepted', 'in_progress']:
        old_technician = session.technician
        session.technician = None
        session.status = 'pending'
        session.priority = 'urgent'
        
        if '[ADVANCED HELP]' not in session.subject:
            session.subject = f"[ADVANCED HELP] {session.subject}"
            
        session.save()
        
        # Add system message
        SessionMessage.objects.create(
            session=session,
            sender=request.user,
            message=f"Session escalated by technician {old_technician}. Returned to queue for advanced help."
        )
        
        messages.warning(request, 'Session escalated and returned to queue.')
        return redirect('support_queue')
    else:
        messages.error(request, 'Cannot escalate a session that is not in progress.')
        return redirect('remote_session_room', session_code=session_code)


@login_required
def my_sessions(request):
    """View user's support session history."""
    sessions = RemoteSupportSession.objects.filter(requester=request.user)
    
    return render(request, 'remote_support/my_sessions.html', {
        'sessions': sessions,
    })


@login_required
@require_POST
def toggle_voice(request, session_code):
    """Toggle voice transcript status."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Check access
    if request.user != session.requester and request.user != session.technician:
        if not is_support_staff(request.user):
            return JsonResponse({'error': 'Access denied'}, status=403)
            
    active = request.POST.get('active') == 'true'
    session.is_voice_active = active
    session.save()
    
    return JsonResponse({'success': True, 'is_voice_active': session.is_voice_active})


@login_required
@require_POST
def save_transcript(request, session_code):
    """Save a chunk of voice transcript."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Check access
    if request.user != session.requester and request.user != session.technician:
        if not is_support_staff(request.user):
            return JsonResponse({'error': 'Access denied'}, status=403)
            
    text = request.POST.get('text', '').strip()
    if text:
        VoiceTranscript.objects.create(
            session=session,
            speaker=request.user,
            text=text
        )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Empty text'}, status=400)


@login_required
def get_full_transcript(request, session_code):
    """Get full voice transcript for the session."""
    session = get_object_or_404(RemoteSupportSession, session_code=session_code)
    
    # Check access
    if request.user != session.requester and request.user != session.technician:
        if not is_support_staff(request.user):
            return JsonResponse({'error': 'Access denied'}, status=403)
            
    transcripts = session.voice_transcripts.all().order_by('created_at')
    
    return JsonResponse({
        'transcripts': [
            {
                'speaker': t.speaker.get_full_name() or t.speaker.username,
                'text': t.text,
                'time': t.created_at.strftime('%H:%M:%S'),
                'is_self': t.speaker == request.user
            }
            for t in transcripts
        ]
    })
