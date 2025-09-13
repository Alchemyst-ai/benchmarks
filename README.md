# Alchemyst Benchmarks

## LongMemEval

### Prep steps (DO NOT SKIP)
Download the [LongMemEval dataset](https://drive.google.com/file/d/1zJgtYRFhOh5zDQzzatiddfjYhFSnyQ80/view?usp=sharing), uncompress it and create folder in ./longmemeval/data, and extract it there.

### Execution Steps
#### Detailed
- Install longmemeval as specified in [**LongMemEval README.md**](./longmemeval/README.md)
- Copy .env.example to .env.local
- Add env vars to .env.local
- Run `custom_call_script.py` to generate answers with your OpenAI API Key, after retrieving information from Alchemyst AI's API Keys.
- Run `dedup.py` to deduplicate data (if any) by question Id and then find missing questions in `missing_questions.json` (if any). (You can edit `custom_call_script.py` to point to `missing_questions.json` as reference file.)
- Run `process_output_before_evaluate_qa.py` on deduped_output.jsonl
- Run `python3 evaluate_qa.py gpt-4o deduped_output_processed.jsonl ../../data/longmemeval_oracle.json >> benchmark_output.log` to get realtime.

#### One-shot execution script
```bash
# Setup environment
cp .env.example .env.local
echo "Add your environment variables to .env.local"

# Run benchmarking pipeline
python3 custom_call_script.py
python3 dedup.py
python3 process_output_before_evaluate_qa.py -i deduped_output.jsonl -o deduped_output_processed.jsonl
python3 evaluate_qa.py gpt-4o deduped_output_processed.jsonl ../../data/longmemeval_oracle.json >> benchmark_output.log
```
