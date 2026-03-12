# OpenCode Model Latency Measurement Tools

A self-contained CLI tool to measure latency of OpenCode available models.

## Usage

```shell
➜  opencode_latency.py -h
usage: opencode_latency.py [-h] [--providers [PROVIDERS ...]] [--models [MODELS ...]] [--iterations ITERATIONS] [--timeout TIMEOUT]

Measure latency of OpenCode models

options:
  -h, --help            show this help message and exit
  --providers [PROVIDERS ...]
                        Specific providers to test, default to all available providers
  --models [MODELS ...]
                        Specific model to test, can not be used with --providers
  --iterations ITERATIONS
                        Number of iterations per model
  --timeout TIMEOUT     Timeout in seconds for each model iteration
```

## Example Results

```
| Model / Latency (s) of Iteration |     1 |     2 |     3 |
|----------------------------------------------------------|
| volcengine/ark-code-latest       | 10.34 | 11.12 | 16.96 |
| volcengine/deepseek-v3.2         | 14.82 | 14.07 | 22.16 |
| volcengine/doubao-seed-2.0-code  | 12.02 | 16.01 | 22.64 |
| volcengine/doubao-seed-2.0-lite  | 14.19 | 14.92 | 14.45 |
| volcengine/doubao-seed-2.0-pro   | 16.73 | 19.46 | 20.46 |
| volcengine/doubao-seed-code      | 18.28 | 13.39 | 11.33 |
| volcengine/glm-4.7               | 20.67 | 13.02 | 18.23 |
| volcengine/kimi-k2.5             | 10.19 | 10.51 | 21.69 |
| volcengine/minimax-m2.5          | Timeout | 18.44 | 13.17 |
```

## Refs

- utilizes [OpenCode CLI](./docs/opencode-cli.md) tool
