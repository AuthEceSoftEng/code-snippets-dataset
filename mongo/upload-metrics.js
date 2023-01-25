import "dotenv/config";

import fs from "node:fs";
import path from "node:path";

import mongoose from "mongoose";
import csv from "csv-parser";

import Snippet from "./snippet.js";
import AnalysisMetrics from "./analysisMetrics.js";
import Violations from "./violations.js";
import ReadabilityMetrics from "./readabilityMetrics.js";

const { MONGODB_URI, RESULTS_PATH, DATASET_PATH, ASTS_PATH, CLUSTERS_PATH } = process.env;

// Connect to db
const db = await mongoose.connect(MONGODB_URI).catch((error_) => {
    console.error(error_.message);
});

// Function to read a csv file and transform it to array
const readCSV = async (filepath, options) => {
    const data = [];
    try {
        const readStream = fs.createReadStream(filepath);
        const parser = readStream.pipe(csv({ separator: ";", ...options }));
        for await (const row of parser) {
            data.push(row);
        }
    } catch (err) {
        console.error(err);
    }
    return data;
}

// Read the files with the metrics calculated
const analysismetrics = (await readCSV("../libs/metrics.csv", { headers: false })).map((m) => m["0"]);
const violations = (await readCSV("../libs/violations.csv", { headers: false })).map((v) => v["0"]);
const readabilitymetrics = JSON.parse(fs.readFileSync("../libs/readabilitymetrics.json"));
const clusters = await readCSV(path.join(CLUSTERS_PATH, "clusters.csv"), { separator: "," });

const files = fs.readdirSync(RESULTS_PATH);
for (const [ind, file] of files.entries()) {
    const fileType = file.split("_")[1];
    const number = file.split("_")[2].split(".csv")[0];
    const codeFile = ((fs.readFileSync(path.join(DATASET_PATH, fileType, `java_${fileType}_${number}.jsonl`), 'utf8')).toString()).split("\n").map((l) => JSON.parse(l));
    const snippets = await readCSV(path.join(RESULTS_PATH, file));
    const asts = await readCSV(path.join(ASTS_PATH, `java_${fileType}_${number}_ast.csv`), { separator: "," });
    for (const [snipInd, snippet] of snippets.entries()) {
        console.log(`File ${ind + 1} out of ${files.length} - Snippet ${snipInd + 1}/${snippets.length}`);
        const code = codeFile.find((el) => snippet.url === el.url);
        const ast = asts.find((el) => snippet.url === el.url);
        const clusterID = clusters?.find((cl) => cl.url === snippet.url)?.cluster;
        try {
            await Snippet.create({
                url: snippet.url,
                type: fileType,
                repo: code.repo,
                sha: code.sha,
                path: code.path,
                functionName: code.func_name,
                code: code.code,
                docstring: code.docstring,
                codeTokens: code.code_tokens,
                docstringTokens: code.docstring_tokens,
                ast: ast.ast,
                astCode: ast.ast_code,
                clusterID: (clusterID && clusterID !== "-") && clusterID,
            });
            await AnalysisMetrics.create({
                url: snippet.url,
                ...Object.fromEntries(analysismetrics.map((m) => ([m, parseFloat(snippet[m])]))),
            });
            await Violations.create({
                url: snippet.url,
                ...Object.fromEntries(violations.map((v) => ([v, parseFloat(snippet[v])]))),
            });
            await ReadabilityMetrics.create({
                url: snippet.url,
                ...Object.fromEntries(Object.keys(readabilitymetrics).map((r) => ([r, Object.fromEntries(Object.keys(readabilitymetrics[r]).map((el) => ([el, parseFloat(snippet[`${r}_${el}`])])))]))),
            });
        } catch { /* empty */ }
    }
}

// Close db connection
db.disconnect();
