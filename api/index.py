import requests
from flask import Flask, request, Response

app = Flask(__name__)

# ═══ CHANGE THIS TO YOUR ACTUAL STREAMLIT CLOUD URL ═══
STREAMLIT_URL = "https://arc-eight.streamlit.app"  # <-- replace if different
# ══════════════════════════════════════════════════════

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target = f"{STREAMLIT_URL}/{path}" if path else STREAMLIT_URL

    # Build headers (strip 'host' to avoid conflicts)
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}

    # Forward the request exactly as received
    try:
        resp = requests.request(
            method=request.method,
            url=target,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,   # we handle redirects manually
            timeout=30               # Vercel max is 10s for hobby, but we set 30 to be safe
        )
    except requests.exceptions.Timeout:
        return "Proxy timeout – Streamlit app may be slow", 504
    except requests.exceptions.RequestException as e:
        return f"Proxy error: {str(e)}", 502

    # If the response is a redirect, follow it (but we need to keep our domain)
    # Streamlit often redirects to '/' from '/'
    if resp.status_code in (301, 302, 303, 307, 308):
        location = resp.headers.get('Location')
        if location:
            # Make location absolute
            if location.startswith('/'):
                location = f"{STREAMLIT_URL}{location}"
            # Recursively fetch the final content
            try:
                final_resp = requests.get(location, headers=headers, cookies=request.cookies, timeout=30)
                # Return the final response (we keep the status 200, but you can pass the status)
                return Response(final_resp.content, status=final_resp.status_code, headers=dict(final_resp.headers))
            except:
                return "Failed to follow redirect", 500

    # Prepare response headers (remove problematic ones)
    response_headers = dict(resp.headers)
    response_headers.pop('Content-Encoding', None)   # avoid double gzip
    response_headers.pop('Transfer-Encoding', None)
    # Optionally remove X-Frame-Options if you want to embed (but not needed)

    # Return the response
    return Response(resp.content, status=resp.status_code, headers=response_headers)