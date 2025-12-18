import fs from "fs";
import { GoogleGenerativeAI } from "@google/generative-ai";
import AlchemystAI from "@alchemystai/sdk";
import { encoding_for_model } from "tiktoken";


const MODEL_NAME = "gemini-2.5-flash";
const OUTPUT_DIR = "./alchemystSearchResult";


const encoder = encoding_for_model("gpt-4");
function countTokens(text: string): number {
  return encoder.encode(text).length;
}

const queries = JSON.parse(
  fs.readFileSync("queries.json", "utf-8")
) as { id: number; content: string }[];

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

const alchemyst = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY!,
  baseURL: "https://platform-dev.getalchemystai.com",
});

const model = genAI.getGenerativeModel({
  model: MODEL_NAME,
  tools: [
    {
      functionDeclarations: [
        {
          name: "alchemyst_protocol",
          description:
            "Perform semantic search over indexed repository using Alchemyst",
          parameters: {
            type: "object",
            properties: {
              query: { type: "string" },
            },
            required: ["query"],
          },
        },
      ],
    },
  ],
});


async function runAlchemyst(query: string): Promise<string> {
  const res = await alchemyst.v1.context.search({ 
    query,
    similarity_threshold: 0.5, 
    minimum_similarity_threshold: 0.3,
    body_metadata: {

    }
  });
  
  return JSON.stringify(res.contexts.slice(0, 3), null, 2);
}

async function run() {
  for (let i = 0; i < queries.length; i++) {
    const q = queries[i];

    const response = await model.generateContent(
      `Call alchemyst_protocol for the following query:

"${q.content}"`
    );

    const call = response.response.functionCalls()?.[0];
    if (!call) continue;

    const output = await runAlchemyst(call.args.query);

    const queryTokens = countTokens(q.content);
    const outputTokens = countTokens(output);

    const result = {
      id: q.id,
      query: q.content,
      tool: "alchemyst",
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

    console.log(`ALCHEMYST saved: query_${q.id}.json`);
  }
}

run().catch(console.error);

