import AlchemystAI from "@alchemystai/sdk";

const alchemystClient = new AlchemystAI({
    apiKey: process.env.ALCHEMYST_AI_API_KEY!,
    baseURL: "https://platform-dev.getalchemystai.com",
})


async function inspect() {
    const docs = await alchemystClient.v1.context.view.docs();


    console.log(JSON.stringify(docs, null, 2))
}

inspect().catch(console.error)