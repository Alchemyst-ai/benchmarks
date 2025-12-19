Tested on the opencode codebase
commit id: b07a47fc89b6ca662c4f6b536d6f0c0ec5890f89

Benchmark: grep vs Alchemyst Context Search (opencode)

Folder structure:
benchmark-testing/
├── benchmark_grep.ts
├── benchmark_alchemystSearch.ts
├── compareResults.ts
├── mergeAlchemystResults.ts
├── queries.json
├── README.md

Prerequisites
- Node.js or Bun

Environment variables:
export GEMINI_API_KEY=your_gemini_key
export ALCHEMYST_AI_API_KEY=your_alchemyst_key

Step 1: Define queries
Edit queries.json to define the benchmark questions.
[
    {"content": "How does the plugin system work in opencode?", "id": 1 },
    {"content": "How do we add an agent to opencode?", "id": 2},
]
Each query must have:
- a unique id
- a natural-language question

Step 2: Run the grep benchmark
This script:
- converts each question into a keyword using Gemini
- runs grep on the opencode repository
- stores results by query ID
Run:
bun benchmark_grep.ts
Output:
- Individual result files in grepResult/
- Or a merged grepResult.json (depending on setup)

Step 3: Run the Alchemyst benchmark
This script:
- sends the full question to Alchemyst
- performs semantic context search
- filters results to the opencode-benchmark group
- records token usage
Run:
bun benchmark_alchemystSearch.ts
Output:
- Individual result files in alchemystSearchResult/
- Or a merged alchemystSearchResult.json

Step 5: Compare results
To align and compare grep and Alchemyst outputs by query ID:
Run:
bun compareResults.ts
This produces a comparison file showing:
- matched queries
- token usage
- output size
Only queries present on both sides are compared.

Notes:
Token counts use tiktoken as an approximation

Summary:
1. Define queries in queries.json
2. Run benchmark_grep.ts
3. Run benchmark_alchemystSearch.ts
4. Compare outputs

