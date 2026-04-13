#!/usr/bin/env python3
"""Run the canonical reprobridge materializer and persist JSON output artifacts."""

from materialize_reprobridges import main_with_output_capture


if __name__ == "__main__":
    raise SystemExit(main_with_output_capture())
