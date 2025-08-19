from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

NAGAD_URL = "https://app2.mynagad.com:20002/api/user/check-user-status-for-log-in"

@app.route("/check", methods=["POST"])
def check_user():
    try:
        data = request.get_json()
        number = data.get("msisdn")

        if not number or not number.isdigit() or len(number) != 11 or not number.startswith("01"):
            return jsonify({"error": "Invalid Bangladeshi number format"}), 400

        params = {"msisdn": number}
        headers = {
            'X-KM-User-AspId': '100012345612345',
            'X-KM-User-Agent': 'ANDROID/1164',
            'X-KM-DEVICE-FGP': '5AB18952A962A31MM9A89524F6282F78905DDE9F94656B5C1CFCEDNN74AE660E',
            'X-KM-Accept-language': 'bn',
            'X-KM-AppCode': '01',
            'Host': 'app2.mynagad.com:20002',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.14.9'
        }

        response = requests.get(NAGAD_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"{response.status_code}: {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return " Nagad Checker Backend is running. Use POST /check"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)