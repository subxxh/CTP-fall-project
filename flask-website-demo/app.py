from flask import Flask, request, render_template
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.download_songs import download_audio
from scripts.extract_librosa_features import extract_features as extract_features_annoy
from scripts.extract_librosa_features_GTZAN import extract_features as extract_features_GTZAN
from scripts.recommendation_service import RecommendationService
from genre_model.inference import GenreModel

# Flask App
app = Flask(__name__)

# Toggle debug mode here, skips youtube download and uses test.wav but still goes through analysis
DEBUG_MODE = False

# Load models once at startup
recommender = RecommendationService(model_dir="annoy_similarity/model/")
classifier = GenreModel(artifact_dir="genre_model/artifacts")

# Placeholder audio for debug mode
DEBUG_AUDIO_PATH = PROJECT_ROOT / "flask-website-demo" / "test.wav"
DEBUG_EMBED_URL = "https://www.youtube.com/embed/dQw4w9WgXcQ"  # example


# ROUTES
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if not user_input and not DEBUG_MODE:
            return render_template("index.html", error="No song URL or text entered.")

        # Download audio from input (or skip in debug)
        if DEBUG_MODE:
            downloaded_path = DEBUG_AUDIO_PATH
            embed_url = DEBUG_EMBED_URL
        else:
            download = download_audio(user_input)
            downloaded_path = download[0]
            embed_url = download[1]
            if downloaded_path is None:
                return render_template("index.html", error="Could not download audio.")

        try:
            # Extract Features
            annoy_features = extract_features_annoy(downloaded_path)
            GTZAN_features = extract_features_GTZAN(downloaded_path)

            # Recommendations
            result_df = recommender.recommend_from_features(annoy_features, k=10)
            results = result_df.to_dict(orient="records")

            for result in results:
                accuracy = result["distance"] * 100
                full = 10 - int(accuracy / 10)
                half = 1 if float(accuracy - full) >= 0.5 else 0
                empty = 10 - full - half
                result["hearts"] = {"full": full, "half": half, "empty": empty}

            # Genre Classification
            genre_list = classifier.top_k(GTZAN_features, k=1)
            top_genre = genre_list[0]["genre"] if genre_list else "Unknown"

        finally:
            # Cleanup only if not in debug mode
            if not DEBUG_MODE and downloaded_path.exists():
                downloaded_path.unlink()

        return render_template("index.html", results=results, genre=top_genre, embed_url=embed_url)

    return render_template("index.html")


# MAIN
if __name__ == "__main__":
    app.run(debug=True)
