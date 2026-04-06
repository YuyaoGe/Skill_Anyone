"""Audio transcription using whisper.cpp via pywhispercpp."""

import json
from pathlib import Path


def transcribe_audio(
    audio_path: str, output_dir: str, config: dict
) -> str:
    """Transcribe an audio file using whisper.cpp.

    Returns path to the output JSON transcript.
    """
    from pywhispercpp.model import Model

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model_name = config.get("model", "medium")
    n_threads = config.get("threads", 6)

    model = Model(model_name, n_threads=n_threads)

    segments = model.transcribe(audio_path)

    transcript_segments = []
    full_text_parts = []

    for seg in segments:
        segment_data = {
            "start": seg.t0,
            "end": seg.t1,
            "text": seg.text.strip(),
        }
        transcript_segments.append(segment_data)
        full_text_parts.append(seg.text.strip())

    stem = Path(audio_path).stem
    transcript = {
        "video_id": stem,
        "source": "whisper",
        "model": model_name,
        "text": " ".join(full_text_parts),
        "segments": transcript_segments,
    }

    out_file = output_path / f"{stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    return str(out_file)
