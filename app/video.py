import os
import re
import shutil
import subprocess
from urllib.parse import urlparse, parse_qs

import requests


def _is_youtube(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host.endswith("youtube.com") or host == "youtu.be" or host.endswith(".youtu.be")


def _is_gdrive(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host.endswith("drive.google.com")


def _gdrive_file_id(url: str) -> str:
    """Pull the file id out of common Google Drive URL formats."""
    m = re.search(r"/file/d/([^/]+)/", url)
    if m:
        return m.group(1)
    qs = parse_qs(urlparse(url).query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    raise ValueError(f"Could not extract Google Drive file id from URL: {url!r}")


def _download_gdrive(url: str, dest_dir: str) -> str:
    file_id = _gdrive_file_id(url)
    session = requests.Session()
    base = "https://drive.google.com/uc"

    resp = session.get(base, params={"export": "download", "id": file_id}, stream=True, timeout=60)
    # Large files get an HTML interstitial with a confirm token.
    token = None
    for k, v in resp.cookies.items():
        if k.startswith("download_warning"):
            token = v
            break
    if token:
        resp.close()
        resp = session.get(
            base,
            params={"export": "download", "id": file_id, "confirm": token},
            stream=True,
            timeout=60,
        )

    out = os.path.join(dest_dir, f"gdrive_{file_id}.mp4")
    with open(out, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    return out


def _download_youtube(url: str, dest_dir: str) -> str:
    from yt_dlp import YoutubeDL  # imported lazily
    out_template = os.path.join(dest_dir, "yt_%(id)s.%(ext)s")
    opts = {
        "outtmpl": out_template,
        "format": "mp4/best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
    return path


def _download_direct(url: str, dest_dir: str) -> str:
    name = os.path.basename(urlparse(url).path) or "video.mp4"
    out = os.path.join(dest_dir, name)
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(out, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    return out


def download_video(link: str, dest_dir: str) -> str:
    """Download a video to dest_dir and return its filesystem path."""
    os.makedirs(dest_dir, exist_ok=True)
    if _is_gdrive(link):
        return _download_gdrive(link, dest_dir)
    if _is_youtube(link):
        return _download_youtube(link, dest_dir)
    return _download_direct(link, dest_dir)


def compress_video(input_path: str, output_path: str) -> str:
    """Re-encode the video to a smaller size suitable for Gemini upload.

    If ffmpeg is missing, return the original path unchanged.
    """
    if shutil.which("ffmpeg") is None:
        return input_path

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "scale=-2:480",
        "-c:v", "libx264",
        "-crf", "28",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-b:a", "64k",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed to compress video:\n" + result.stderr.decode("utf-8", errors="ignore")
        )
    return output_path
