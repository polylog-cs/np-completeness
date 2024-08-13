import argparse
import shutil
from pathlib import Path

QUALITY = "2160p60"


def main(output_dir: Path):
    videos = list(Path(__file__).parents[1].glob(f"media/videos/*/{QUALITY}/*.mp4"))

    if output_dir.exists():
        if input(f"{output_dir} already exists. Overwrite? (y/n) ").lower() != "y":
            shutil.rmtree(output_dir)
            exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    for video in videos:
        shutil.copy(video, output_dir / video.name)

    print(f"Copied {len(videos)} videos to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    main(args.output_dir)
