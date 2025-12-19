import fs from "fs";
import { execSync } from "child_process";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { encoding_for_model } from "tiktoken";

const REPO_PATH = "./opencode";
const MODEL_NAME = "gemini-2.5-flash";
const OUTPUT_DIR = "./grepResult";


const encoder = encoding_for_model("gpt-4");
function countTokens(text: string): number {
  return encoder.encode(text).length;
}

const queries = JSON.parse(
  fs.readFileSync("queries.json", "utf-8")
) as { id: number; content: string }[];


const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

const model = genAI.getGenerativeModel({
  model: MODEL_NAME,
  tools: [
    {
      functionDeclarations: [
        {
          name: "grep_protocol",
          description:
            "Convert a natural language question into a single keyword for grep search",
          parameters: {
            type: "object",
            properties: {
              keyword: { type: "string" },
            },
            required: ["keyword"],
          },
        },
      ],
    },
  ],
});

function runGrep(keyword: string): string {
  try {
    return execSync(
      `grep -R -n -i "${keyword}" ${REPO_PATH}`,
      { encoding: "utf-8", maxBuffer: 1024 * 1024 }
    ).slice(0, 5000);
  } catch {
    return "No matches found";
  }
}

async function run() {
  for (let i = 0; i < queries.length; i++) {
    const q = queries[i];

    const response = await model.generateContent(
      `Convert the following question into a grep keyword and call grep_protocol:

"${q.content}"`
    );

    const call = response.response.functionCalls()?.[0];
    if (!call) continue;

    const output = runGrep(call.args.keyword);

    const queryTokens = countTokens(q.content);
    const outputTokens = countTokens(output);

    const result = {
      id: q.id,
      query: q.content,
      tool: "grep",
      keyword: call.args.keyword,
      tokens: {
        query: queryTokens,
        output: outputTokens,
        total: queryTokens + outputTokens,
      },
      output,
    };

    fs.writeFileSync(
      `${OUTPUT_DIR}/query_${q.id}.json`,
      JSON.stringify(result, null, 2)
    );

    console.log(`GREP saved: query_${q.id}.json`);
  }
}

run().catch(console.error);
