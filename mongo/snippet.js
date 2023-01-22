import mongoose from "mongoose";

const { Schema, model } = mongoose;

const snippetSchema = new Schema(
	{
		url: { type: String, required: true },
        type: { type: String, required: true, enum: ["train", "test", "valid"] },
        repo: { type: String },
        sha: { type: String },
        path: { type: String },
        functionName: { type: String },
        code: { type: String },
        docstring: { type: String },
        codeTokens: [{ type: String }],
        docstringTokens: [{ type: String }],
        analysisMetrics: { type: Object },
        violations: { type: Object },
        readabilityMetrics: { type: Object },
        ast: { type: String },
        astCode: { type: String },
	},
	{ timestamps: true, toObject: { versionKey: false } },
);

export default model("snippets", snippetSchema);
