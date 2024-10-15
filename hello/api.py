from flask import Blueprint, jsonify  # jsonify 추가

...

@bp.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200