# Coding Evaluation Harness

A transparent prototype that evaluates coding submissions by running task tests in Docker, applying an explicit rubric, and producing an auditable score report.

## Why I built it

I want to explore how coding evaluations can be reproducible, evidence-based, and open to review rather than producing unexplained scores.

## Input format

Tasks and submissions use JSON Lines (JSONL): one JSON object per line. I chose JSONL because it is easy to inspect in Git, append in batch workflows, and process one record at a time at scale.
