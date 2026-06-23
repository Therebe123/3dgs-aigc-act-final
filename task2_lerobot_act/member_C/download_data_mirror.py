from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote

from calvin_act.io import write_json


META_FILES = ["conversion.json", "episodes.jsonl", "episodes_stats.jsonl", "info.json", "modality.json", "tasks.jsonl"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="xiaoma26/calvin-lerobot")
    parser.add_argument("--mirror", default="https://hf-mirror.com")
    parser.add_argument("--output-dir", default="data/calvin_lerobot")
    parser.add_argument("--splits", nargs="+", default=["splitA", "splitB", "splitC", "splitD"])
    parser.add_argument("--max-episodes", type=int)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--workers", type=int, default=16)
    return parser.parse_args()


def file_url(mirror: str, repo_id: str, path: str) -> str:
    return f"{mirror.rstrip('/')}/datasets/{repo_id}/resolve/main/{quote(path, safe='/')}"


def fetch(mirror: str, repo_id: str, output_dir: Path, path: str) -> str:
    dst = output_dir / path
    if dst.exists() and dst.stat().st_size > 0:
        return path
    dst.parent.mkdir(parents=True, exist_ok=True)
    url = file_url(mirror, repo_id, path)
    cmd = [
        "wget",
        "-q",
        "-c",
        "--timeout=60",
        "--tries=5",
        "-O",
        str(dst),
        url,
    ]
    subprocess.run(cmd, check=True)
    return path


def parallel_fetch(mirror: str, repo_id: str, output_dir: Path, files: list[str], workers: int, label: str) -> list[str]:
    done = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(fetch, mirror, repo_id, output_dir, path) for path in files]
        for future in as_completed(futures):
            done.append(future.result())
            if len(done) % 50 == 0 or len(done) == len(files):
                print(f"{label}: downloaded {len(done)}/{len(files)}")
    return sorted(done)


def split_files(output_dir: Path, split: str, max_episodes: int | None, full: bool) -> list[str]:
    meta = [f"{split}/meta/{name}" for name in META_FILES]
    info_path = output_dir / split / "meta" / "info.json"
    if not info_path.exists():
        return meta
    info = json.loads(info_path.read_text(encoding="utf-8"))
    total = int(info["total_episodes"]) if full else int(max_episodes or 0)
    chunks_size = int(info.get("chunks_size", 1000))
    episodes = []
    for episode_index in range(total):
        chunk = episode_index // chunks_size
        episodes.append(f"{split}/data/chunk-{chunk:03d}/episode_{episode_index:06d}.parquet")
    return meta + episodes


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"repo_id": args.repo_id, "mirror": args.mirror, "splits": {}, "mode": "full" if args.full else "subset"}

    for split in args.splits:
        meta = [f"{split}/meta/{name}" for name in META_FILES]
        parallel_fetch(args.mirror, args.repo_id, output_dir, meta, min(args.workers, len(meta)), f"{split} meta")
        files = split_files(output_dir, split, args.max_episodes, args.full)
        episode_files = [f for f in files if "/data/" in f]
        if not args.full and args.max_episodes is None:
            raise ValueError("--max-episodes is required unless --full is set")
        downloaded = parallel_fetch(args.mirror, args.repo_id, output_dir, episode_files, args.workers, split)
        manifest["splits"][split] = {"downloaded_files": len(downloaded), "episodes": len(downloaded)}

    write_json(output_dir / "download_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
