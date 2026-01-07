import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

# Mock environment variables for auth
os.environ["OTHELLO_USER_ID"] = "1"
os.environ["OTHELLO_SECRET_KEY"] = "debug_secret"

try:
    from api import app, handle_message
    from flask import json, session

    with app.test_request_context(
        path='/api/message',
        method='POST',
        data=json.dumps({"message": "Hello", "channel": "auto", "client_message_id": "debug-1"}),
        content_type='application/json'
    ):
        session['authed'] = True
        session['user_id'] = '1'
        
        print("Simulating /api/message...")
        response = handle_message()
        # handle_message returns a Response object or a tuple
        if hasattr(response, 'get_data'):
            print("Response:", response.get_data(as_text=True))
            print("Status:", response.status_code)
        else:
            print("Response object:", response)

except Exception as e:
    import traceback
    traceback.print_exc()
