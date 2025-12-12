"""
Extract frames from mp4 files with ffmpeg and build sprite sheets with Pillow.

Usage:
  python make_sprite_sheets.py
  python make_sprite_sheets.py --columns 8 --output-dir spritesheets

Requirements:
  - ffmpeg binary at ./bin/ffmpeg.exe (override with --ffmpeg)
  - Pillow installed: python -m pip install pillow
"""

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


def extract_frames(ffmpeg_path: Path, video_path: Path, frames_dir: Path) -> None:
    frames_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(ffmpeg_path),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-vsync",
        "0",
        str(frames_dir / "frame_%04d.png"),
    ]
    subprocess.run(cmd, check=True)


def build_sprite_sheet(frames_dir: Path, columns: int, output_path: Path) -> None:
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        raise RuntimeError(f"No frames found in {frames_dir}")

    with Image.open(frame_files[0]) as first_frame:
        frame_width, frame_height = first_frame.size

    total_frames = len(frame_files)
    cols = max(1, columns or math.ceil(math.sqrt(total_frames)))
    rows = math.ceil(total_frames / cols)

    sheet = Image.new("RGBA", (frame_width * cols, frame_height * rows))

    for idx, frame_file in enumerate(frame_files):
        with Image.open(frame_file) as frame:
            x = (idx % cols) * frame_width
            y = (idx // cols) * frame_height
            sheet.paste(frame, (x, y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create sprite sheets from mp4 files.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("."),
        help="Directory containing mp4 files (default: current directory).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("spritesheets"),
        help="Directory to write sprite sheets (default: spritesheets).",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=0,
        help="Number of columns in the sprite sheet. If 0, a square-ish grid is used.",
    )
    parser.add_argument(
        "--ffmpeg",
        type=Path,
        default=Path("bin/ffmpeg.exe"),
        help="Path to ffmpeg binary (default: bin/ffmpeg.exe).",
    )
    parser.add_argument(
        "--keep-frames",
        action="store_true",
        help="Keep extracted frame files instead of deleting the temp folder.",
    )
    args = parser.parse_args()

    if not args.ffmpeg.exists():
        raise FileNotFoundError(f"ffmpeg not found at {args.ffmpeg}")

    mp4_files = sorted(args.input_dir.glob("*.mp4"))
    if not mp4_files:
        raise FileNotFoundError(f"No mp4 files found in {args.input_dir}")

    for video_path in mp4_files:
        print(f"Processing {video_path.name}...")
        with tempfile.TemporaryDirectory(prefix=video_path.stem + "_frames_") as tmpdir:
            frames_dir = Path(tmpdir)
            extract_frames(args.ffmpeg, video_path, frames_dir)
            output_path = args.output_dir / f"{video_path.stem}_sheet.png"
            build_sprite_sheet(frames_dir, args.columns, output_path)
            if args.keep_frames:
                # Persist frames to a sibling directory for inspection.
                persist_dir = args.output_dir / f"{video_path.stem}_frames"
                persist_dir.mkdir(parents=True, exist_ok=True)
                for frame_file in sorted(frames_dir.glob("frame_*.png")):
                    frame_file.rename(persist_dir / frame_file.name)
            print(f"  -> {output_path}")


if __name__ == "__main__":
    main()
