import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TERRAFORM = ROOT / "terraform"


def run(*args: str) -> None:
    subprocess.run(list(args), cwd=TERRAFORM, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision an isolated AI Film Studio environment")
    parser.add_argument("command", choices=["plan", "apply", "destroy"])
    parser.add_argument("--film-id", required=True)
    parser.add_argument("--environment-id", required=True)
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    parser.add_argument("--auto-approve", action="store_true")
    args = parser.parse_args()

    common = ["terraform", args.command, "-var", f"film_id={args.film_id}", "-var", f"environment_id={args.environment_id}", "-var", f"aws_region={args.region}"]
    if args.command == "apply" and args.auto_approve:
        common.append("-auto-approve")
    run(*common)

if __name__ == "__main__":
    main()
