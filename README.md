# Alchemyst Benchmarks

This repository contains a collection of benchmarks used to evaluate and compare different systems, approaches, and workflows in a reproducible manner.

The primary goals of this repository are **clarity**, **fair comparison**, and **reproducibility**.

---

## Repository Structure

```text
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
```

---

## Available Benchmarks

### 1. OpenCode: `grep` vs Alchemyst Search

**Location:** `benchmark-testing/`
**Documentation:** `benchmark-testing/README.md`

This benchmark compares two approaches for searching a real-world codebase (**OpenCode**):

* **Keyword-based search** using `grep`
* **Semantic context search** using **Alchemyst**

#### What this benchmark evaluates

* Relevance vs. noise in returned context
* Token usage and cost trade-offs
* Practical search effectiveness in real codebases

For setup instructions and execution steps, refer to:
`benchmark-testing/README.md`

---

### 2. LongMemEval

**Location:** `longmemeval/`
**Documentation:** `longmemeval/README.md`

**LongMemEval** is a comprehensive benchmark designed to evaluate long-term memory capabilities of chat assistants.

#### Key aspects

* Multi-session reasoning
* Temporal reasoning
* Knowledge updates
* Abstention behavior

#### Additional details

* Includes released datasets
* Provides evaluation scripts
* Contains baseline pipelines
* Based on the **LongMemEval paper (ICLR 2025)**

For full setup and execution instructions, see:
`longmemeval/README.md`

---

## 🛠️ General Usage

1. Choose a benchmark folder
2. Read the `README.md` inside that folder
3. Follow the documented setup and execution steps
4. Run the benchmark locally
5. Inspect and compare results

---

## 🤝 Contributing

Contributions are welcome!

When adding a new benchmark:

* Create a new folder under `benchmarks/`
* Include a clear and complete `README.md`
* Document assumptions and limitations
* Keep result artifacts out of Git

---

## Summary

This repository serves as a shared benchmarking space for evaluating different systems and approaches under real-world conditions.

For benchmark-specific details, always refer to the `README.md` inside the corresponding benchmark folder.
