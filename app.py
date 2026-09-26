# ==========================================
# TRAINREADY - FLASK BACKEND
# ==========================================

from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import tempfile

import numpy as np
import pandas as pd

from analyzer import load_dataset, analyze_dataset


# ==========================================
# CREATE FLASK APP
# ==========================================

app = Flask(__name__)

CORS(app)


# ==========================================
# MAKE DATA JSON SAFE
# ==========================================

def make_json_safe(value):

    # Dictionary
    if isinstance(value, dict):

        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }


    # List / Tuple
    if isinstance(value, (list, tuple)):

        return [
            make_json_safe(item)
            for item in value
        ]


    # Boolean
    if isinstance(value, (np.bool_, bool)):

        return bool(value)


    # Integer
    if isinstance(value, np.integer):

        return int(value)


    # Float
    if isinstance(value, np.floating):

        if np.isnan(value) or np.isinf(value):

            return None

        return float(value)


    # Pandas missing value
    try:

        if pd.isna(value):

            return None

    except Exception:

        pass


    return value


# ==========================================
# ANALYZE DATASET
# ==========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # --------------------------------------
    # CHECK FILE
    # --------------------------------------

    if "file" not in request.files:

        return jsonify({
            "error": "No dataset file was uploaded."
        }), 400


    file = request.files["file"]


    # --------------------------------------
    # CHECK FILE NAME
    # --------------------------------------

    if file.filename == "":

        return jsonify({
            "error": "No dataset file was selected."
        }), 400


    # --------------------------------------
    # ALLOWED FILE TYPES
    # --------------------------------------

    allowed_extensions = {
        ".csv",
        ".xlsx",
        ".xls"
    }


    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in allowed_extensions:

        return jsonify({
            "error": "Only CSV, XLSX, and XLS files are supported."
        }), 400


    # --------------------------------------
    # TEMPORARY FILE
    # --------------------------------------

    temp_path = None


    try:

        # Create temporary file

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            file.save(temp_file.name)

            temp_path = temp_file.name


        # ----------------------------------
        # LOAD DATASET
        # ----------------------------------

        df = load_dataset(temp_path)


        # ----------------------------------
        # ANALYZE DATASET
        # ----------------------------------

        report = analyze_dataset(
            df,
            file.filename
        )


        # ----------------------------------
        # MAKE JSON SAFE
        # ----------------------------------

        report = make_json_safe(report)


        # ----------------------------------
        # SEND REPORT TO FRONTEND
        # ----------------------------------

        return jsonify(report), 200


    except Exception as error:

        print(
            "Analysis error:",
            error
        )


        return jsonify({
            "error": str(error)
        }), 500


    finally:

        # ----------------------------------
        # DELETE TEMPORARY FILE
        # ----------------------------------

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            try:

                os.remove(temp_path)

            except Exception:

                pass


# ==========================================
# HOME / SERVER CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "TrainReady backend is running."
    })


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )