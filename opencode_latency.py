#!/usr/bin/python3

import argparse
import subprocess
import sys
import time

PROMPTS = [
    "Hi, how are you?",
    "What is the capital of France?",
    "How many days are in a leap year?",
    "What is 15 * 7?",
    "How many letters in “apple”?",
    "Write one sentence: I am ready.",
    "What is the square root of 144?",
    "What color is the sky?",
    "What is the largest ocean on Earth?",
    "What year did World War II end?",
    "Say “hello”.",
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Measure latency of OpenCode models")
    parser.add_argument(
        "--providers",
        nargs="*",
        help="Specific providers to test, default to all available providers",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        help="Specific model to test, can not be used with --providers",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations per model",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each model iteration",
    )

    args = parser.parse_args()

    if args.providers and args.models:
        print("Error: providers and models can not be used together")
        sys.exit(1)

    if args.iterations > len(PROMPTS):
        print(f"Error: iterations cannot exceed number of prompts ({len(PROMPTS)})")
        sys.exit(1)

    return args


def run_opencode_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")

    except Exception:
        print("Warning: no models found for provider")

    return []


def get_models_from_providers(providers: list[str] | None):
    if not providers:
        return run_opencode_command(["opencode", "models"])

    models = []
    for provider in providers:
        models.extend(run_opencode_command(["opencode", "models", provider]))

    return models


def measure_model_latency(model, timeout, prompt) -> float | str:
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            ["opencode", "run", prompt, "--agent", "plan", "--model", model],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0:
            return time.perf_counter() - start_time

    except subprocess.TimeoutExpired:
        return "Timeout"

    except Exception:
        return "Exception"

    return "Error Code"


def measure_model_latencies(model, timeout, iterations):
    latencies = []
    for i in range(iterations):
        latencies.append(measure_model_latency(model, timeout, prompt=PROMPTS[i]))

    return latencies


def print_header(iterations):
    header = "| Model / Latency (s) of Iteration |"
    for i in range(1, iterations + 1):
        header += f" {i:5} |"
    print(header)
    print("|" + "-" * (len(header) - 2) + "|")


def print_latencies(model, latencies):
    row = f"| {model:32} |"
    for latency in latencies:
        if latency is None:
            row += " Error |"
        else:
            row += f" {latency:5.2f} |"
    print(row)


def main():
    args = parse_arguments()
    models = get_models_from_providers(args.providers)

    print_header(args.iterations)
    for model in models:
        latencies = measure_model_latencies(model, args.timeout, args.iterations)
        print_latencies(model, latencies)

    print("")
    print("done!")


if __name__ == "__main__":
    main()
