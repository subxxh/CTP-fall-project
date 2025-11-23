# Context Entry CTX-EXTRACT

- File: `scripts/extract_librosa_features.py`
- Purpose: load MP3/WAV, compute MFCC/chroma/spectral/RMS/ZCR stats matching `fma_metadata_features_joined.csv` columns (no `track_id`), return dict or DataFrame for downstream scoring.
- Key functions:
	- `_matrix_stats`: mean/std per feature vector.
	- `extract_features(path, sample_rate=22050, hop_length=512, duration=None)`: single-file dict.
	- `_iter_audio_paths` + `extract_many(inputs, pattern="**/*.wav", ...)`: walk files/dirs, emit DataFrame with `source_path` column.
	- `_parse_args`/`main`: CLI wrapper, saves CSV to `--output` (default `data/librosa_features.csv`).
- Usage note: Flask frontend should import `extract_features`, save uploads temporarily, call the function, then delete temp files; CLI reserved for batch/offline runs.
- Tests: see `tests/test_extract_librosa_features.py` (synthetic tone fixture, silent-audio rejection, directory handling, CLI smoke). Latest run `python -m pytest` ⇒ pass (warnings from librosa on short tones only).

# Context Entry CTX-ANNOY

- Folder: `annoy_similarity/`
- Purpose: build and serve an Annoy-based nearest-neighbor engine over FMA feature vectors for recommendation lookup.
- Pipeline overview:
	- `build_index.py`: reads `data/processed/fma_metadata_features_joined.csv`, keeps feature columns matching prefixes (`mfcc_`, `chroma_cqt_`, `spectral_`, `rmse_`, `zcr_`), scales with `StandardScaler`, emits `model/scaler.pkl`, `model/features.npy`, `model/metadata.csv`, and builds `model/ann_index.ann` (50 trees, Euclidean metric).
	- `annoy_engine.py`: `SpotifyAnnoyEngine` loads scaler/features/metadata/index, exposes `query_by_track_index`, `query_by_features` (scales raw feature vector), and `lookup(track_id)` helpers.
	- `validate_model.py`: reruns scaling + compares saved metadata/features + Annoy vectors to original DF; run after building to ensure alignment.
- Usage note: instantiate `SpotifyAnnoyEngine` once per service process, reuse for queries; ensure uploaded audio features are scaled via stored scaler before calling `query_by_features`.

# Context Entry CTX-RECSVC

- File: `scripts/recommendation_service.py`
- Purpose: wraps librosa feature extraction and the Annoy engine into a minimal service class for backend routes.
- Components:
	- `_FEATURE_NAMES` / `_vector_from_feature_map`: enforce feature ordering expected by the scaler/Annoy index.
	- `RecommendationService`: methods `recommend_from_audio`, `recommend_from_features`, `recommend_from_track_id`, `build_response_payload`; accepts optional pre-built `SpotifyAnnoyEngine` for DI/testing.
- Usage note: instantiate once in `app.py`, reuse across requests; supply `audio_path` (MP3/WAV) or an existing feature map/track_id to get a pandas `DataFrame` of neighbors with appended `distance` column.
- Tests: `tests/test_recommendation_service.py` (dummy Annoy engine to verify vector wiring and method behavior). Suite passes via `python -m pytest`.

# Context Entry CTX-GTZAN

- Package: `genre_model/` (modules `config.py`, `training.py`, `inference.py`, plus `__init__.py` re-exports) and CLI `scripts/train_genre_model.py`.
- Purpose: GTZAN RandomForest classifier with clean separation between configuration, training/artifact handling, and inference helpers for Flask routes.
- Components:
	- `config.py`: `TrainingConfig` dataclass + shared constants (target column, dropped columns, artifact filenames, default artifact dir).
	- `training.py`: `load_dataset`, `_feature_columns`, pipeline builder (StandardScaler + RandomForest), `TrainingResult`, `train_and_evaluate`, `save_artifacts`, `load_feature_names`.
	- `inference.py`: `GenreModel` loads persisted artifacts, validates incoming feature maps, and exposes `predict`, `predict_proba`, `top_k`.
	- CLI `scripts/train_genre_model.py`: wraps `TrainingConfig` & `train_and_evaluate`, persists artifacts, prints validation accuracy. Legacy `scripts/genre_model.py` now re-exports the package for backward compatibility.
- Tests: `tests/test_genre_model.py` covers training, artifact serialization, inference, probability normalization, and missing-feature guards.


