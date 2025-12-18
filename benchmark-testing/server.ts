import { glob } from "glob";
import { readFile, stat } from "fs/promises";
import path from "path";
import AlchemystAI from "@alchemystai/sdk";



const OPENCODE_BASE_REPO = "./opencode";

const alchemystClient = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY!,
  baseURL: "https://platform-dev.getalchemystai.com"
});

const sleep = (ms: number) =>
  new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  const files = await glob(`${OPENCODE_BASE_REPO}/**/*.*`, {
    nodir: true,
  });

  const contents = [];

  for (const file of files) {
    const stats = await stat(file);

    
    if (!file.match(/\.(ts|js|md|json|txt)$/)) continue;

    const content = await readFile(file, "utf-8");

    contents.push({
      content,
      metadata: {
        groupName: [...file.split(path.sep), "opencode-benchmark"],
        fileType: "text/plain",
        fileName: file,
        fileSize: stats.size,
        lastModified: stats.mtime.toISOString()
      },
    });
  }
  console.log(contents.length);
  for (let i = 0; i < contents.length; i += 5) {
    const batch = contents.slice(i, i + 5);

    for (const item of batch) {
      await alchemystClient.v1.context.add({
        documents: [{ content: item.content }],
        context_type: "resource",
        source: "opencode",
        scope: "internal",
        metadata: item.metadata,
      });
    }

    await sleep(3000);
  }

  console.log("Repo indexing completed");
}

main().catch(console.error);
