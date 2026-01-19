from flask import Flask, render_template, request
import pandas as pd
from topsis import topsis
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

# 🔐 CHANGE THESE
import os

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def send_email(receiver, file_path):
    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver
    msg.set_content("Attached is your TOPSIS result.")

    with open(file_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="topsis_result.csv"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("SENDER_EMAIL", "APP_PASSWORD")
        server.send_message(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    table = None
    error = None

    if request.method == "POST":
       try:
            file = request.files["file"]
            email = request.form["email"]
            weights = list(map(float, request.form["weights"].split(",")))
            impacts = request.form["impacts"].split(",")

            df = pd.read_csv(file)

            # ✅ VALIDATION (HERE)
            if len(weights) != df.shape[1] - 1:
                raise Exception("Number of weights must match number of criteria")

            if len(impacts) != df.shape[1] - 1:
                raise Exception("Number of impacts must match number of criteria")

            if not all(i in ['+', '-'] for i in impacts):
                raise Exception("Impacts must be + or - only")

            result = topsis(df, weights, impacts)

            os.makedirs("output", exist_ok=True)
            output_file = "output/topsis_result.csv"
            result.to_csv(output_file, index=False)

            send_email(email, output_file)
            table = result.to_html(index=False)

       except Exception as e:
        error = str(e)


    return render_template("index.html", table=table, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

   

