import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import requests
from openai import OpenAI
from tqdm import tqdm

CHECKPOINTS_DIR = Path("./checkpoints")

REFERENCE_FILE = "../../data/longmemeval_oracle.json"
OUTPUT_FILE = CHECKPOINTS_DIR / "first_hypothesis_test.log"
API_URL = "https://platform-backend.getalchemystai.com/api/v1/context/search"  # <-- Change to your system's endpoint
CONTEXT_API_HEADERS = {
    "Authorization": f"Bearer {os.getenv('ALCHEMYST_AI_API_KEY', '')}"
}

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    os.getenv("OPENAI_API_KEY"),
)

OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def get_answer_from_api(question):
    # Modify this payload and headers as per your API spec
    payload = {
        "query": question,
        "metadata": None,
        "similarity_threshold": 0.6,
    }
    response = requests.post(API_URL, json=payload, headers=CONTEXT_API_HEADERS)

    if (
        response.ok
        # or not response.json()["contexts"]
    ):
        response_json = response.json()
        # Fallback to OpenAI if API fails or returns no answer
        openai_prompt = f"""Given the data, answer the following question:
        {question}

        The data is:
        ```
        {[x.get("content") for x in response_json.get("contexts", [])[:10]]}
        ```
        """
        completion = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": openai_prompt}],
            temperature=0.0,
        )
        print(response_json.keys())
        print(f"Fetched {len(response_json.get('contexts', []))} contexts")
        ans = completion.choices[0].message.content
        print("Received responses = ")
        print(ans)
        return ans.strip() if ans is not None else ""
    else:
        print("Error: ", response.status_code)
        print(response.text)
        response.raise_for_status()
    # Adjust this if your API returns a different field
    # return response.json()["answer"]


def main():
    parser = argparse.ArgumentParser(description="Run evaluation with optional offset.")
    parser.add_argument(
        "--offset", type=int, default=0, help="Start processing from this offset"
    )
    args = parser.parse_args()

    with open(REFERENCE_FILE, "r") as f:
        questions = json.load(f)

    offset = args.offset
    questions = questions[offset:]
    answers = []
    saved_idx = 0
    try:
        checkpoint_file = ""
        with open(OUTPUT_FILE, "w") as out_f:
            for idx, q in enumerate(
                tqdm(questions, initial=offset, total=len(questions) + offset)
            ):
                answer = ""
                try:
                    answer = get_answer_from_api(q["question"])
                    print("Received answer = ")
                except Exception as e:
                    print(f"Error for {q['question_id']}: {e}")
                    answer = ""
                result = {
                    "question_id": q["question_id"],
                    "hypothesis": answer,
                    "idx": idx,
                }
                out_f.write(json.dumps(result) + "\n")
                saved_idx = idx
                answers.append(answer)

                # Save checkpoint every 5 entries
                if (idx + 1) % 5 == 0 or idx:
                    checkpoint_file = f"saved_checkpoint_{offset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    print(f"\nSaving checkpoint to {checkpoint_file}")
                    with open(checkpoint_file, "w") as ckpt_f:
                        for i in range(saved_idx + 1):
                            result = {
                                "question_id": questions[i]["question_id"],
                                "hypothesis": answers[i],
                                "idx": i
                                + offset,  # This is already correct as it shows absolute position
                            }
                            ckpt_f.write(json.dumps(result) + "\n")
                    print("Checkpoint saved.")

    except KeyboardInterrupt:
        checkpoint_file = (
            f"saved_checkpoint_{offset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        print(f"\nInterrupted! Saving progress to {checkpoint_file}")
        with open(checkpoint_file, "w") as ckpt_f:
            for i in range(saved_idx + 1):
                result = {
                    "question_id": questions[i]["question_id"],
                    "hypothesis": answers[i],
                    "idx": offset + i,
                }
                ckpt_f.write(json.dumps(result) + "\n")
        print("Checkpoint saved. Exiting.")


if __name__ == "__main__":
    main()
