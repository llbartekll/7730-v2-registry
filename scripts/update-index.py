#!/usr/bin/env python3
"""Update index.json with entries for lifi and safe registry descriptors."""

import json
import os

REGISTRY_ROOT = os.path.join(os.path.dirname(__file__), "..")
INDEX_PATH = os.path.join(REGISTRY_ROOT, "index.json")

FOLDERS = ["registry/lifi", "registry/safe", "registry/weth"]


def make_key(chain_id: int, address: str) -> str:
    return f"eip155:{chain_id}:{address.lower()}"


def extract_deployments(descriptor: dict) -> list[dict]:
    ctx = descriptor.get("context", {})
    if "contract" in ctx:
        return ctx["contract"].get("deployments", [])
    if "eip712" in ctx:
        return ctx["eip712"].get("deployments", [])
    return []


def main():
    with open(INDEX_PATH) as f:
        index = json.load(f)

    # Normalize existing string values to arrays
    for key in index:
        if isinstance(index[key], str):
            index[key] = [index[key]]

    added = 0
    for folder in FOLDERS:
        abs_folder = os.path.join(REGISTRY_ROOT, folder)
        if not os.path.isdir(abs_folder):
            print(f"Skipping {folder} (not found)")
            continue

        for filename in sorted(os.listdir(abs_folder)):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(abs_folder, filename)
            rel_path = f"{folder}/{filename}"

            with open(filepath) as f:
                descriptor = json.load(f)

            deployments = extract_deployments(descriptor)
            if not deployments:
                continue

            for dep in deployments:
                key = make_key(dep["chainId"], dep["address"])
                paths = index.setdefault(key, [])
                if rel_path not in paths:
                    paths.append(rel_path)
                    print(f"  + {key} -> {rel_path}")
                    added += 1

    # Collapse single-element arrays back to strings for compactness
    for key in index:
        if isinstance(index[key], list) and len(index[key]) == 1:
            index[key] = index[key][0]

    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")

    print(f"\nDone. Added {added} entries to index.json.")


if __name__ == "__main__":
    main()
