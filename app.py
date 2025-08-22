from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=20)  # একসাথে 20 concurrent requests

NAGAD_URL = "https://app2.mynagad.com:20002/api/user/check-user-status-for-log-in"

def fetch_nagad(number):
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
    params = {"msisdn": number}
    try:
        response = requests.get(NAGAD_URL, headers=headers, params=params, timeout=30, verify=False)
        if response.status_code == 200:
            result = response.json()
            result["api_owner"] = "Shadow Joker"
            result["number"] = number
            return result
        else:
            return {
                "error": f"{response.status_code}: {response.text}",
                "api_owner": "Shadow Joker",
                "number": number
            }
    except requests.Timeout:
        return {"error": "Request timed out after 30 seconds", "api_owner": "Shadow Joker", "number": number}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}", "api_owner": "Shadow Joker", "number": number}

@app.route("/check", methods=["POST"])
def check_user():
    data = request.get_json()
    numbers = data.get("numbers")  # batch mode: list of numbers
    single_number = data.get("msisdn") or data.get("number")  # single mode fallback

    if single_number:
        numbers = [single_number]

    if not numbers or not isinstance(numbers, list):
        return jsonify({
            "error": "Provide 'msisdn' or 'number' for single check OR 'numbers' list for batch check",
            "api_owner": "Shadow Joker"
        }), 400

    valid_numbers = []
    invalid_numbers = []

    for num in numbers:
        if not num or not num.isdigit() or len(num) != 11 or not num.startswith("01"):
            invalid_numbers.append(num)
        else:
            valid_numbers.append(num)

    results = []
    futures = {executor.submit(fetch_nagad, num): num for num in valid_numbers}

    for future in as_completed(futures):
        results.append(future.result())

    if invalid_numbers:
        for num in invalid_numbers:
            results.append({
                "error": "Invalid Bangladeshi number format",
                "api_owner": "Shadow Joker",
                "number": num
            })

    return jsonify(results)

@app.route("/")
def home():
    return "Nagad Checker Backend is running. Use POST /check | API owner: Shadow Joker"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
