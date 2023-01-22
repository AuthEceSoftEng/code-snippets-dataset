import mongoose from "mongoose";

const { Schema, model } = mongoose;

const analysisMetricsSchema = new Schema(
	{
		url: { type: String, required: true, unique: true },
	},
	{ timestamps: true, toObject: { versionKey: false }, strict: false },
);

export default model("analysisMetrics", analysisMetricsSchema);
