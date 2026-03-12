# OpenCode Model Latency Measurement Tools

A CLI tool to measure latency of OpenCode available models.

## Design

- use TTFT (Time To First Token) to measure model latency
- utilizes [OpenCode CLI](./docs/opencode-cli.md) to test models
- is a single Python script without external dependencies.
- can test multiple models in parallel
- can handle errors gracefully

## Installation

## Usage

```shell
opencode_ttft.py [-h] [--providers PROVIDERS...] [--models MODELS...] [--iterations ITERATIONS] [--timeout TIMEOUT] [--thread THREAD]

# Test  models from providers
opencode-ttft --providers opencode volcengine

# Test specific models
opencode-ttft --models opencode/kimi-k2.5 volcengine/glm-4.7 opencode/kimi-k2.5

# Custom prompt, iterations and timeout
opencode-ttft --models opencode/kimi-k2.5 --prompt "Explain quantum computing" --iterations 3 --timeout 60
```

## Example Results

```shell
## Condition

| Argument   | Value                                                    |
| ---------- | -------------------------------------------------------- |
| Providers  | opencode volcengine                                      |
| Models     | opencode/kimi-k2.5 volcengine/glm-4.7 opencode/kimi-k2.5 |
| Prompt     | "Explain quantum computing"                              |
| Iterations | 3                                                        |
| Timeout    | 60                                                       |

## Progress

Testing volcengine/glm-4.7 ... 4.23s
Testing opencode/kimi-k2.5 ... 3.45s
Testing opencode/kimi-k2.5 ... Error

## Result

| Model              | Average TTFT (s) | Max TTFT (s) |
| ------------------ | ---------------- | ------------ |
| opencode/kimi-k2.5 | 3.45             | 3.45         |
| volcengine/glm-4.7 | 4.23             | 4.23         |
| opencode/kimi-k2.5 | Error            | Error        |
```

**Notes**

- Results are rounded to 2 decimal places (in seconds)
- Results are sorted by TTFT in ascending order
- Timeout/Error models are marked with `Error` and placed at the end of the table
