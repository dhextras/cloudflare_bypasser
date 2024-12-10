import os
from functools import wraps

import dotenv
from flask import Flask, jsonify, request

from bypass_cloudflare import bypasser

# Load environment variables & Initialize Falsk App
dotenv.load_dotenv()
EXPECTED_API_KEY = os.getenv("CLOUDFLARE_BYPASS_SERVER_API_KEY")

app = Flask(__name__)


def require_api_key(view_function):
    """
    Decorator to require API key authentication
    """

    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # Check if API key is present in headers or query parameters
        api_key = request.headers.get("Server-API-Key") or request.args.get("api_key")

        if not api_key or api_key != EXPECTED_API_KEY:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized: Invalid or missing API key",
                    }
                ),
                401,
            )

        return view_function(*args, **kwargs)

    return decorated_function


@app.route("/bypass", methods=["POST"])
@require_api_key
def bypass_cloudflare():
    """
    Endpoint to bypass Cloudflare for a given URL
    """
    data = request.json

    if not data or "url" not in data:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    url = data["url"]

    try:
        result = bypasser(url)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.errorhandler(500)
def handle_500(error):
    """
    Catch-all error handler
    """

    return (
        jsonify(
            {"status": "error", "message": "Internal server error", "error": str(error)}
        ),
        500,
    )


if __name__ == "__main__":
    if not EXPECTED_API_KEY:
        raise ValueError("CLOUDFLARE_BYPASS_SERVER_API_KEY must be set in environment")

    app.run(host="0.0.0.0", port=5000)
