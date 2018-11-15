"""Utilities to handle sessions.
"""

SADDRESS = 'address'
SLOCATION = 'location'
SLOCATION_ACCURATE = 'location_accurate'
SUSERNAME = 'username'
SUSER_ID = 'user_id'
SUSER_EXPIRATION = 'user_expiration'
SMESSAGE_HISTORY = 'message_history'

def get_message_history(request):
    history = request.session.get(SMESSAGE_HISTORY, None)
    if history is None:
        request.session[SMESSAGE_HISTORY] = []
        history = []
    return history

def add_messages_to_history(request, messages):
    if SMESSAGE_HISTORY in request.session:
        request.session[SMESSAGE_HISTORY] += messages
    else:
        request.session[SMESSAGE_HISTORY] = messages

def clear_message_history(request):
    request.session[SMESSAGE_HISTORY] = []
