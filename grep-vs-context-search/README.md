# Benchmark: `grep` vs Alchemyst Context Search (OpenCode)

This benchmark evaluates **traditional keyword-based search (`grep`)** against **semantic context search (Alchemyst)** on a real-world codebase: **OpenCode**.

The objective is to measure practical differences in:

* Relevance of retrieved context
* Noise vs. signal in results
* Token usage and cost trade-offs
* Usefulness for understanding large repositories

---

## Repository Structure

```
benchmark-testing/
├── benchmark_grep.ts
├── benchmark_alchemystSearch.ts
├── compareResults.ts
├── mergeAlchemystResults.ts
├── queries.json
└── README.md
```

---

## Prerequisites

* **Node.js** or **Bun**
* **OpenCode repository** cloned locally

---

## Environment Variables

Before running the benchmarks, export the following environment variables:

```bash
export GEMINI_API_KEY=your_gemini_api_key
export ALCHEMYST_AI_API_KEY=your_alchemyst_api_key
```

---

## Step 1: Define Benchmark Queries

Edit `queries.json` to specify the questions used for the benchmark.

```json
[
  { "id": 1, "content": "How does the plugin system work in opencode?" },
  { "id": 2, "content": "How do we add an agent to opencode?" }
]
```

Each query must include:

* A **unique numeric ID**
* A **natural-language question**

---

## Step 2: Run the `grep` Benchmark

This script:

* Converts each natural-language question into keywords using **Gemini**
* Runs `grep` against the OpenCode repository
* Stores results mapped to each query ID

### Run

```bash
bun benchmark_grep.ts
```

### Output

* Individual result files in `grepResult/`
* Or a merged `grepResult.json` (depending on configuration)

---

## Step 3: Run the Alchemyst Context Search Benchmark

This script:

* Sends the full natural-language question directly to **Alchemyst**
* Performs **semantic context search**
* Filters results to the `opencode-benchmark` context group
* Records token usage per query

### Run

```bash
bun benchmark_alchemystSearch.ts
```

### Output

* Individual result files in `alchemystSearchResult/`
* Or a merged `alchemystSearchResult.json`

---

## Step 4: Compare Results

To align and compare `grep` and Alchemyst outputs by query ID, run:

```bash
bun compareResults.ts
```

### Comparison Includes

* Queries present in **both** benchmarks
* Retrieved context size
* Token usage (Alchemyst)
* Differences in retrieved content

Only queries available on **both sides** are included in the comparison.

---

## Notes

* Token counts are estimated using **tiktoken** and should be treated as approximations.
* This benchmark emphasizes **real-world usability** over academic retrieval metrics.

---

## Summary

1. Define queries in `queries.json`
2. Run `benchmark_grep.ts`
3. Run `benchmark_alchemystSearch.ts`
4. Compare results with `compareResults.ts`
