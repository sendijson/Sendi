import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

UPSTREAM_URL = "https://followed-accounts-api.vercel.app/info"

@app.route('/', methods=['GET'])
def docs():
    return jsonify({
        "service": "Local Followed Accounts Info Proxy",
        "method": "GET only",
        "endpoints": {
            "/info": {
                "description": "Get followed creators and their craft levels",
                "parameters": {
                    "uid": "Guest UID (optional if using other auth)",
                    "password": "Guest password (optional if using other auth)",
                    "access_token": "Garena access token (optional)",
                    "jwt_token": "Raw JWT token (optional)",
                    "eat_token": "EAT token or callback URL (optional)"
                },
                "examples": [
                    "/info?uid=123456&password=secret",
                    "/info?access_token=YOUR_ACCESS_TOKEN",
                    "/info?jwt_token=YOUR_JWT_TOKEN",
                    "/info?eat_token=YOUR_EAT_TOKEN"
                ]
            }
        }
    })

@app.route('/info', methods=['GET'])
def info():
    uid = request.args.get('uid', '').strip()
    password = request.args.get('password', '').strip()
    access_token = request.args.get('access_token', '').strip()
    jwt_token = request.args.get('jwt_token', '').strip()
    eat_token = request.args.get('eat_token', '').strip()

    if not any([
        (uid and password),
        access_token,
        jwt_token,
        eat_token
    ]):
        return jsonify({
            "status": "error",
            "message": "Provide one of: uid/password, access_token, jwt_token, or eat_token"
        }), 400

    upstream_params = {}
    if uid and password:
        upstream_params['uid'] = uid
        upstream_params['password'] = password
    elif access_token:
        upstream_params['access_token'] = access_token
    elif jwt_token:
        upstream_params['jwt_token'] = jwt_token
    elif eat_token:
        upstream_params['eat_token'] = eat_token

    try:
        upstream_resp = requests.get(UPSTREAM_URL, params=upstream_params, timeout=20)
        upstream_resp.raise_for_status()
        return jsonify(upstream_resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"Upstream error: {str(e)}"}), 502
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid JSON from upstream"}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)