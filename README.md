# OpenCode Model Latency Measurement Tools

A CLI tool for measuring Time To First Token (TTFT) latency of OpenCode models.

TTFT (Time To First Token) is the latency from when a user sends a request to when the first token of the response begins to stream.

## Design

This tool utilizes the [OpenCode CLI](https://opencode.ai/docs/cli) to measure model latency. Here is the core command:

```shell
# List all available models
opencode models

# Test a model
opencode run "Hi, how are you?" --agent plan --model volcengine/minimax-m2.5
```

**Notes**

- Each model test has a 30-second timeout
- Models are tested in parallel
- Errors and timeouts are handled gracefully

## Usage

```shell
# Test all available models
opencode-ttft --all

# Test specific models
opencode-ttft --models opencode/kimi-k2.5 volcengine/glm-4.7 opencode/kimi-k2.5
```

## Example Results

```shell
Testing volcengine/glm-4.7 ... 4.23s
Testing opencode/kimi-k2.5 ... 3.45s
Testing opencode/kimi-k2.5 ... Error

Model Latency:

| Model              | TTFT (s) |
| ------------------ | -------- |
| opencode/kimi-k2.5 | 3.45     |
| volcengine/glm-4.7 | 4.23     |
| opencode/kimi-k2.5 | Error    |
```

**Notes**

- Results are rounded to 2 decimal places (in seconds)
- Results are sorted by TTFT in ascending order
- Timeout/Error models are marked with `Error` and placed at the end of the table
