import argparse
import json


def process_jsonl(input_file: str, output_file: str):
    modified_entries = []

    # Read the JSONL file
    with open(input_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            # Add the new field
            if "autoeval_label" not in entry:
                entry["autoeval_label"] = {}
            entry["autoeval_label"]["model"] = "gpt-4o-2024-08-06"
            modified_entries.append(entry)

    # Write back to the same file
    with open(output_file, "w") as f:
        for entry in modified_entries:
            f.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Process JSONL file and add model label"
    )
    parser.add_argument(
        "-i", "--input_file", help="Input JSONL file path", required=True
    )
    parser.add_argument(
        "-o", "--output_file", help="Output JSONL file path", required=True
    )
    args = parser.parse_args()

    process_jsonl(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
