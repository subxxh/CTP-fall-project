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
	- `build_index.py`: reads `data/fma_metadata_features_joined.csv`, keeps feature columns matching prefixes (`mfcc_`, `chroma_cqt_`, `spectral_`, `rmse_`, `zcr_`), scales with `StandardScaler`, emits `model/scaler.pkl`, `model/features.npy`, `model/metadata.csv`, and builds `model/ann_index.ann` (50 trees, Euclidean metric).
	- `annoy_engine.py`: `SpotifyAnnoyEngine` loads scaler/features/metadata/index, exposes `query_by_track_index`, `query_by_features` (scales raw feature vector), and `lookup(track_id)` helpers.
	- `validate_model.py`: reruns scaling + compares saved metadata/features + Annoy vectors to original DF; run after building to ensure alignment.
- Usage note: instantiate `SpotifyAnnoyEngine` once per service process, reuse for queries; ensure uploaded audio features are scaled via stored scaler before calling `query_by_features`.


