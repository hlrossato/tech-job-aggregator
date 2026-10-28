#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "src"))

from jobboard.application.services import ExpireJobsService
from jobboard.infrastructure.repositories.sqlalchemy import SQLAlchemyUnitOfWork


def main() -> None:
    parser = argparse.ArgumentParser(description="Expire jobs not seen since the cutoff")
    parser.add_argument("source_key")
    parser.add_argument("--hours", type=int, default=48)
    args = parser.parse_args()
    cutoff = datetime.now(UTC) - timedelta(hours=args.hours)
    count = ExpireJobsService(SQLAlchemyUnitOfWork()).expire_unseen(args.source_key, cutoff)
    print(f"expired {count} jobs for {args.source_key}")


if __name__ == "__main__":
    main()
