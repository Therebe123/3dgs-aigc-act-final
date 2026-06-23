from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from huggingface_hub import HfApi

from calvin_act.dataset import describe_local_splits
from calvin_act.io import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="xiaoma26/calvin-lerobot")
    parser.add_argument("--data-root", default="data/calvin_lerobot")
    parser.add_argument("--output", default="artifacts/dataset_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    info = HfApi().dataset_info(args.repo_id, files_metadata=True)
    by_split = defaultdict(lambda: {"files": 0, "bytes": 0, "types": Counter()})
    for sibling in info.siblings:
        path = sibling.rfilename
        if "/" not in path:
            continue
        split = path.split("/", 1)[0]
        rec = by_split[split]
        rec["files"] += 1
        rec["bytes"] += getattr(sibling, "size", 0) or 0
        if path.endswith(".parquet"):
            rec["types"]["parquet"] += 1
        elif path.endswith(".json") or path.endswith(".jsonl"):
            rec["types"]["json"] += 1
        else:
            rec["types"]["other"] += 1
    remote = {
        split: {
            "files": rec["files"],
            "size_gb": round(rec["bytes"] / 1024**3, 3),
            "types": dict(rec["types"]),
        }
        for split, rec in sorted(by_split.items())
    }
    data = {
        "repo_id": args.repo_id,
        "revision": info.sha,
        "remote": remote,
        "local": describe_local_splits(args.data_root, ["splitA", "splitB", "splitC", "splitD"]),
    }
    write_json(args.output, data)
    print(data)


if __name__ == "__main__":
    main()
