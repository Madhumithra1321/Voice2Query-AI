import json
import time
from pathlib import Path

import requests

from app.config import (
    SPEECHMATICS_API_KEY,
    SPEECHMATICS_BATCH_URL,
    SPEECHMATICS_LANGUAGE,
)


def _extract_transcript(transcript_json: dict) -> str:
    words = []
    for result in transcript_json.get("results", []):
        alternatives = result.get("alternatives") or []
        if alternatives:
            content = alternatives[0].get("content", "")
            if content:
                words.append(content)
    return " ".join(words).strip()


def transcribe_audio_file(audio_path: str | Path) -> tuple[str | None, str | None]:
    if not SPEECHMATICS_API_KEY:
        return None, "SPEECHMATICS_API_KEY is not set yet."

    path = Path(audio_path)
    if not path.exists():
        return None, f"Audio file not found: {path}"

    headers = {"Authorization": f"Bearer {SPEECHMATICS_API_KEY}"}
    config = {
        "type": "transcription",
        "transcription_config": {"language": SPEECHMATICS_LANGUAGE},
    }

    try:
        with path.open("rb") as audio_file:
            response = requests.post(
                f"{SPEECHMATICS_BATCH_URL}/jobs",
                headers=headers,
                files={
                    "data_file": (path.name, audio_file),
                    "config": (None, json.dumps(config)),
                },
                timeout=60,
            )
        response.raise_for_status()
        job_id = response.json()["id"]

        for _ in range(60):
            status_response = requests.get(
                f"{SPEECHMATICS_BATCH_URL}/jobs/{job_id}",
                headers=headers,
                timeout=30,
            )
            status_response.raise_for_status()
            status = status_response.json()["job"]["status"]

            if status == "done":
                transcript_response = requests.get(
                    f"{SPEECHMATICS_BATCH_URL}/jobs/{job_id}/transcript",
                    headers=headers,
                    params={"format": "json-v2"},
                    timeout=30,
                )
                transcript_response.raise_for_status()
                transcript = _extract_transcript(transcript_response.json())
                return transcript, None

            if status == "rejected":
                return None, "Speechmatics rejected the transcription job."

            time.sleep(2)

        return None, "Speechmatics transcription timed out."
    except Exception as exc:
        return None, f"Speechmatics error: {exc}"


def listen_to_voice():
    return "Speechmatics is configured for uploaded audio files in the Streamlit app."
