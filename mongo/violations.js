import mongoose from "mongoose";

const { Schema, model } = mongoose;

const violationsSchema = new Schema(
	{
		url: { type: String, required: true, unique: true },
	},
	{ timestamps: true, toObject: { versionKey: false }, strict: false },
);

export default model("violations", violationsSchema);
