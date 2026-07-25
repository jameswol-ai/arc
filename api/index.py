import requests
from flask import Flask, request, Response

app = Flask(__name__)

# ═══ CHANGE THIS TO YOUR ACTUAL STREAMLIT CLOUD URL ═══
STREAMLIT_URL = "https://ai-arc.streamlit.app"
# ══════════════════════════════════════════════════════

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target = f"{STREAMLIT_URL}/{path}" if path else STREAMLIT_URL

    # Forward the request
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}

    try:
        resp = requests.request(
            method=request.method,
            url=target,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )
    except requests.exceptions.Timeout:
        return "Proxy timeout – Streamlit app may be slow", 504
    except requests.exceptions.RequestException as e:
        return f"Proxy error: {str(e)}", 502

    # Handle redirects
    if resp.status_code in (301, 302, 303, 307, 308):
        location = resp.headers.get('Location')
        if location and location.startswith('/'):
            location = f"{STREAMLIT_URL}{location}"
        try:
            final_resp = requests.get(location, headers=headers, cookies=request.cookies, timeout=30)
            response_headers = dict(final_resp.headers)
            response_headers.pop('Content-Encoding', None)
            response_headers.pop('Transfer-Encoding', None)
            return Response(final_resp.content, status=final_resp.status_code, headers=response_headers)
        except:
            return "Failed to follow redirect", 500

    response_headers = dict(resp.headers)
    response_headers.pop('Content-Encoding', None)
    response_headers.pop('Transfer-Encoding', None)

    return Response(resp.content, status=resp.status_code, headers=response_headers)
