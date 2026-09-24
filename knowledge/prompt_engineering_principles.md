# Prompt Engineering Principles & Best Practices

## 1. Instruction Hierarchy & Delimiters
Always separate instructions from input context using clear delimiters:
- Use Markdown triple backticks or XML tags (`<context>`, `<instructions>`, `<input>`).
- Specify output structure and negative constraints explicitly.

## 2. Role and Perspective Scoping
Assign a clear persona or domain role to establish vocabulary, reasoning depth, and perspective:
- Good: "Act as a Principal Distributed Systems Engineer..."
- Poor: "Give me some tech advice..."

## 3. Negative Constraints & Boundary Setting
Negative prompting prevents common failure modes:
- For text: Explicitly forbid conversational fluff, corporate buzzwords, and unsubstantiated claims.
- For diffusion models: Exclude deformities, blur, duplicate anatomy, and watermarks.

## 4. Format Anchoring
Declare the desired structural format before generating content:
- Request JSON schemas with field definitions for machine-to-machine pipelines.
- Request Markdown tables for comparative trade-off analyses.
