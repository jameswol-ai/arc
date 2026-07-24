from flask import Flask, request, Response
import requests
import re

app = Flask(__name__)

# Replace with your actual Streamlit Cloud URL (without trailing slash)
STREAMLIT_URL = "https://your-app-name.streamlit.app"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target = f"{STREAMLIT_URL}/{path}" if path else STREAMLIT_URL

    # Forward the request
    resp = requests.request(
        method=request.method,
        url=target,
        headers={key: value for key, value in request.headers.items() if key.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )

    # If the response is a redirect, follow it (but we want to stay on our domain)
    if resp.is_redirect:
        # Resolve the redirect location and return it as a response
        location = resp.headers.get('Location')
        if location.startswith('/'):
            location = f"{STREAMLIT_URL}{location}"
        # Return a redirect to the same path on our domain? No – just fetch the new location
        # Better: just return the response as is (the browser will follow)
        # We'll handle by making a new request to the redirect location
        return proxy(location.replace(STREAMLIT_URL, '').lstrip('/'))

    # Modify response headers if needed (remove X-Frame-Options to allow iframe, etc.)
    headers = dict(resp.headers)
    headers.pop('Content-Encoding', None)  # avoid gzip issues
    headers.pop('Transfer-Encoding', None)
    # Optionally remove X-Frame-Options if you need to embed (but not necessary)

    # Return the response
    return Response(resp.content, status=resp.status_code, headers=headers)