from django.contrib.sessions.models import Session


def delete_user_session(user_id: int):
    sessions = Session.objects.all()
    for session in sessions:
        session_data = session.get_decoded()
        if str(user_id) == session_data.get('_auth_user_id', None):
            session.delete()
