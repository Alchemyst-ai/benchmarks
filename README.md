Alchemyst Benchmarks

This repository contains a collection of benchmarks used to evaluate and
compare different systems, approaches, and workflows in a reproducible way.

The goal of this repo is clarity and comparibility.

Repository structure

benchmarks/
├── benchmark-testing/
│   └── README.md
│
├── longmemeval/
│   ├── README.md
│   └── src/
│
├── .gitignore
└── README.md

Available benchmarks

1. opencode: grep vs Alchemyst search
Location: benchmark-testing/
See: benhmark-testing/README.md
for setup instructions and usage
This benchmark compares two approaches for searching a real codebase
(opencode):
- Keyword search using grep
- Semantic context search using Alchemyst

It focuses on understanding:
- relevance vs noise in returned context
- token usage trade-offs

For details on how to run this benchmark, see:
benchmark-testing/README.md

2. LongMemEval
Location: longmemeval/

LongMemEval is a comprehensive benchmark for evaluating long-term memory
capabilities of chat assistants.

- Tests multi-session reasoning, temporal reasoning, knowledge updates, and abstention
- Includes released datasets, evaluation scripts, and baseline pipelines
- Originates from the LongMemEval paper (ICLR 2025)

For full setup and execution steps, see:
longmemeval/README.md

🛠️ General Usage
1. Choose a benchmark folder
2. Read the README inside that folder
3. Follow the documented setup and execution steps
4. Inspect or compare results locally

🤝 Contributing
Contributions are welcome.
When adding a new benchmark:
- create a new folder
- include a clear README
- document assumptions and limitations
- keep result artifacts out of Git

Summary
This repository serves as a shared space for benchmarking different approaches
and systems under real-world conditions.
For benchmark-specific details, always refer to the README inside the
corresponding folder.