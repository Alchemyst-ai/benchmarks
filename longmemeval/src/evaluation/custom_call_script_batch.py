import argparse
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
from openai import AsyncOpenAI, OpenAI
from tqdm import tqdm

os.makedirs("checkpoints", exist_ok=True)
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
# OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

OPENAI_ASYNC_CLIENT = AsyncOpenAI(api_key=OPENAI_API_KEY)


def save_answers_to_file(queries, filename):
    """
    Save a list of queries (each with 'id', 'hypothesis', 'question_id') to a file as JSON lines.
    """
    with open(filename, "w") as f:
        for query in queries:
            f.write(json.dumps(query) + "\n")


def retry_with_backoff(max_retries=3, backoff=2):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    wait_time = backoff * (2**attempt)
                    print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

        return wrapper

    return decorator


@retry_with_backoff(max_retries=3, backoff=2)
async def make_api_request(
    session: aiohttp.ClientSession, api_url: str, payload: dict[str, Any], idx: int
):
    async with session.post(
        api_url, json=payload, headers=CONTEXT_API_HEADERS
    ) as response:
        if response.status == 200:
            print("Response from ctx proc arrived for index ", idx)
            return ("ok", await response.json())
        else:
            response.raise_for_status()
            return ("error", None)


@retry_with_backoff(3, 2)
async def make_openai_request(contexts, question: str, idx: int, client: AsyncOpenAI):
    openai_prompt = f"""Given the data, answer the following question:
  {question}

  The data is:
  ```
  {[x.get("content") for x in contexts[:10]]}
  ```
  """
    print("Making OpenAI request for idx ", idx)
    completion = await client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": openai_prompt}],
        temperature=0.0,
    )
    print("Received response from OpenAI for idx ", idx)
    return completion.choices[0].message.content


async def get_answer_from_api(session: aiohttp.ClientSession, question: str, idx: int):
    print("Sending request for index: ", idx)

    payload = {"query": question, "metadata": None, "similarity_threshold": 0.6}

    try:
        # Retry API request
        status, response_json = await make_api_request(session, API_URL, payload, idx)

        if status != "ok" or response_json is None:
            raise Exception("API failed to respond.")

        print("\n\n", response_json.keys())
        print(f"Fetched {len(response_json.get('contexts', []))} contexts")

        # Retry OpenAI request
        ans = await make_openai_request(
            response_json.get("contexts", []), question, idx, OPENAI_ASYNC_CLIENT
        )
        print("Received responses = ")
        print(ans)
        return (idx, ans.strip() if ans is not None else "")
    except Exception as e:
        print(f"Error after all retries for idx {idx}: {str(e)}")
        return (idx, "")


async def get_answers_from_api_batch(
    questions, batch_start_offset: int, batch_size: int
):
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(questions), batch_size):
            batch = questions[i : i + batch_size]
            tasks = []
            for idx, q in enumerate(batch):
                try:
                    task = get_answer_from_api(
                        session, q["question"], batch_start_offset + idx
                    )
                    tasks.append(task)
                except Exception as e:
                    print(f"Error creating task for question {idx}: {str(e)}")
                    tasks.append(None)

            batch_answers = []
            for task in tasks:
                if task:
                    try:
                        answer = await task
                        batch_answers.append(answer)
                    except Exception as e:
                        print(f"Error processing answer: {str(e)}")
                        batch_answers.append((None, ""))
                else:
                    batch_answers.append((None, ""))

            for q, ans in zip(batch, batch_answers):
                results.append(
                    {
                        "question_id": q["question_id"],
                        "hypothesis": ans[1] if ans[0] is not None else "",
                        "idx": ans[0] if ans[0] is not None else -1,
                    }
                )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run evaluation with optional offset and batch size."
    )
    parser.add_argument(
        "--offset", type=int, default=0, help="Start processing from this offset"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Number of questions to process in each batch",
    )
    args = parser.parse_args()

    with open(REFERENCE_FILE, "r") as f:
        questions = json.load(f)

    offset = args.offset
    batch_size = args.batch_size
    questions = questions[offset:]
    answers = []
    saved_idx = 0

    try:
        with tqdm(
            total=len(questions) + offset,
            initial=offset,
            mininterval=0.1,
            desc=f"Processing questions (offset={offset})",
        ) as pbar:
            for batch_start in range(0, len(questions), batch_size):
                batch = questions[batch_start : batch_start + batch_size]
                try:
                    batch_answers = asyncio.run(
                        get_answers_from_api_batch(
                            batch, offset + batch_start, batch_size
                        )
                    )

                    # Calculate batch number and create filename
                    batch_number = (batch_start + batch_size) // batch_size
                    output_file = (
                        CHECKPOINTS_DIR
                        / f"batch_{batch_number}_{batch_size}_{offset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    )

                    # Write batch results to file
                    with open(output_file, "w") as batch_f:
                        for ans in batch_answers:
                            batch_f.write(json.dumps(ans) + "\n")
                            answers.append(ans["hypothesis"])

                    saved_idx = batch_start + len(batch_answers) - 1
                    pbar.update(len(batch))

                except Exception as e:
                    print(
                        f"\n\nError for batch starting at {offset + batch_start}: {e}"
                    )
                    batch_number = (batch_start + batch_size) // batch_size
                    error_file = (
                        CHECKPOINTS_DIR
                        / f"error_batch_{batch_number}_{batch_size}_{offset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    )

                    with open(error_file, "w") as error_f:
                        for idx, q in enumerate(batch):
                            result = {
                                "question_id": q["question_id"],
                                "hypothesis": "",
                                "idx": idx + batch_start + offset,
                            }
                            error_f.write(json.dumps(result) + "\n")
                            answers.append("")
                    saved_idx = batch_start + len(batch) - 1
                    pbar.update(len(batch))

    except KeyboardInterrupt:
        final_batch = (saved_idx + batch_size) // batch_size
        checkpoint_file = (
            CHECKPOINTS_DIR
            / f"interrupt_batch_{final_batch}_{batch_size}_{offset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        print(f"\nInterrupted! Saving progress to {checkpoint_file}")
        with open(checkpoint_file, "w") as ckpt_f:
            for i in range(offset, saved_idx + 1):
                result = {
                    "question_id": questions[i - offset]["question_id"],
                    "hypothesis": answers[i - offset][-1]
                    if answers[i - offset] is not None
                    else "",
                    "idx": i,
                }
                ckpt_f.write(json.dumps(result) + "\n")
        print("Checkpoint saved. Exiting.")


if __name__ == "__main__":
    main()
