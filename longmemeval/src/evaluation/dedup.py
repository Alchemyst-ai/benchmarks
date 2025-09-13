import glob

import pandas as pd


def run_dedup():
    # Get all checkpoint log files
    log_files = glob.glob(
        "checkpoints/saved_checkpoint_*.log", recursive=True
    ) + glob.glob("checkpoints/first_hypothesis_test*.log", recursive=True)

    # Read and combine all files
    all_data = []
    for file in log_files:
        with open(file, "r") as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    all_data.append(pd.read_json(line, lines=True))

    # Combine all data and deduplicate
    df = pd.concat(all_data, ignore_index=True)
    df = df.drop_duplicates(subset=["question_id"], keep="last")

    # Export to jsonl
    df.to_json("deduped_output.jsonl", orient="records", lines=True)


def find_diff(question_dataset_filename: str, deduped_dataset_filename: str):
    # Read both files
    questions_df = pd.read_json(question_dataset_filename)
    deduped_df = pd.read_json(deduped_dataset_filename, lines=True)

    # Find ids in questions but not in deduped
    missing_ids = list(
        set(questions_df["question_id"]) - set(deduped_df["question_id"])
    )
    return missing_ids


def extract_questions(question_dataset_filename: str, question_ids: list):
    # Read questions file
    questions_df = pd.read_json(question_dataset_filename)

    # Filter for specified question_ids
    filtered_df = questions_df[questions_df["question_id"].isin(question_ids)]
    return filtered_df


def get_missing_questions(
    question_dataset_filename: str, deduped_dataset_filename: str
):
    # Find missing ids
    missing_ids = find_diff(question_dataset_filename, deduped_dataset_filename)

    # Get corresponding questions
    missing_questions = extract_questions(question_dataset_filename, missing_ids)
    return missing_questions


# Run this to deduplicate
run_dedup()
missing_questions = get_missing_questions(
    "../../data/longmemeval_oracle.json", "deduped_output.jsonl"
)

# Run this to store the missing questions. Then you can run those again with custom_call_script as the reference file.
print("Missing questions = ", missing_questions.shape)
missing_questions.to_json("missing_questions.json", orient="records")
