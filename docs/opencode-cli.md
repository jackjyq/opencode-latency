# OpenCode CLI

## list models

```shell
# List available models
-> opencode models -h
opencode models [provider]

list all available models

Positionals:
  provider  provider ID to filter models by                                                 [string]

Options:
  -h, --help        show help                                                              [boolean]
  -v, --version     show version number                                                    [boolean]
      --print-logs  print logs to stderr                                                   [boolean]
      --log-level   log level                   [string] [choices: "DEBUG", "INFO", "WARN", "ERROR"]
      --verbose     use more verbose model output (includes metadata like costs)           [boolean]
      --refresh     refresh the models cache from models.dev                               [boolean]

# example: list all models
-> opencode models
opencode/big-pickle
opencode/gpt-5-nano
opencode/mimo-v2-flash-free
opencode/minimax-m2.5-free
opencode/nemotron-3-super-free
aisp-coding-plan/glm-5
aisp-coding-plan/kimi-k2.5
aisp-coding-plan/MiniMax-M2.5
aisp-coding-plan/Qwen3-235B-A22B
aisp-coding-plan/Qwen3.5-397B-A17B
volcengine/deepseek-v3.2
volcengine/glm-4.7
volcengine/kimi-k2.5
volcengine/minimax-m2.5

# example: list models by provider
-> opencode models volcengine
volcengine/deepseek-v3.2
volcengine/glm-4.7
volcengine/kimi-k2.5
volcengine/minimax-m2.5
```

## Test models

```shell
# Test a model
opencode run "Hi, how are you?" --agent plan --model volcengine/minimax-m2.5
```

## Refs

- [OpenCode CLI](https://opencode.ai/docs/cli)
