import fs from "fs";

const grepDir = "./grepResult";
const alchemystDir = "./alchemystSearchResult";


/**
 * Loads all JSON files from the given directory and indexes them by their numeric `id` field.
 * Files that do not contain a numeric `id` property are skipped.
 *
 * @param dir - Path to the directory containing JSON result files.
 * @returns A map from `id` to the parsed JSON content for each file.
 */
function loadResultsById(dir: string) {
  const files = fs.readdirSync(dir).filter(f => f.endsWith(".json"));
  const map = new Map<number, any>();

  for (const file of files) {
    const data = JSON.parse(
      fs.readFileSync(`${dir}/${file}`, "utf-8")
    );

    if (typeof data.id !== "number") {
      console.warn(`⚠️ Skipping file without id: ${file}`);
      continue;
    }

    map.set(data.id, data);
  }

  return map;
}


const grepMap = loadResultsById(grepDir);
const alchemystMap = loadResultsById(alchemystDir);


const allIds = new Set<number>([
  ...grepMap.keys(),
  ...alchemystMap.keys(),
]);

const comparison: any[] = [];

for (const id of Array.from(allIds).sort((a, b) => a - b)) {
  const grepData = grepMap.get(id);
  const alchemystData = alchemystMap.get(id);

  if (!grepData || !alchemystData) {
    console.warn(
      `Incomplete result for query id=${id} ` +
      `(grep=${!!grepData}, alchemyst=${!!alchemystData})`
    );
    continue;
  }

  comparison.push({
    id,
    query: grepData.query,
    grep: {
      keyword: grepData.keyword,
      tokens: grepData.tokens.total,
      outputLength: grepData.output.length,
    },
    alchemyst: {
      tokens: alchemystData.tokens.total,
      outputLength: alchemystData.output.length,
    },
  });
}


fs.writeFileSync(
  "comparison.json",
  JSON.stringify(comparison, null, 2)
);

console.log(
  `comparison.json generated (${comparison.length} aligned queries)`
);
