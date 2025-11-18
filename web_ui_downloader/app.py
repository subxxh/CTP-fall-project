from flask import Flask, request, render_template
from test import main  # your download logic

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    result_url = None
    full = half = empty = accuracy = 0

    if request.method == "POST":
        user_input = request.form.get("user_input")  
        accuracy_input = request.form.get("accuracy")  
        hidden_url = request.form.get("track_url")  

        # If a new track URL is submitted, download
        if user_input:
            result = main(user_input)
            result_url = user_input  # store for hearts form
        else:
            result_url = hidden_url  # keep previous track URL
            # Only trigger hearts update if no new URL
            result = None

        # Compute hearts
        if accuracy_input is not None:
            accuracy = int(accuracy_input)
            full = accuracy // 10
            half = 1 if accuracy % 10 >= 5 else 0
            empty = 10 - full - half

    return render_template(
        "index.html",
        result=result,
        result_url=result_url,
        full=full,
        half=half,
        empty=empty,
        accuracy=accuracy
    )

if __name__ == "__main__":
    app.run(debug=True)
