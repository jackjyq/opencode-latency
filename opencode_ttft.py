#!/usr/bin/python3

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean

PROMPTS = [
    "Hi, how are you?",
    "What is the capital of France?",
    "How many days are in a leap year?",
    "What is 15 * 7?",
    "Who wrote Romeo and Juliet?",
    "What is the boiling point of water in Celsius?",
    "What is the square root of 144?",
    "How many planets are in our solar system?",
    "What is the largest ocean on Earth?",
    "What year did World War II end?",
    "What is the chemical symbol for gold?",
]


def validate_iterations(value):
    ivalue = int(value)
    if ivalue > len(PROMPTS):
        raise argparse.ArgumentTypeError(
            f"iterations ({ivalue}) cannot exceed number of prompts ({len(PROMPTS)})"
        )
    return ivalue


def parse_arguments():
    parser = argparse.ArgumentParser(description="Measure TTFT of OpenCode models")
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
        default=1,
        help="Number of iterations per model",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each model iteration",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Max number of parallel threads, default to 1",
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
        pass
    return []


def get_models_from_providers(providers: list[str] | None):
    if not providers:
        return run_opencode_command(["opencode", "models"])

    models = []
    for provider in providers:
        models.extend(run_opencode_command(["opencode", "models", provider]))

    return models


def measure_ttft(model, prompt, timeout):
    start_time = time.time()
    first_token_time = None
    process = None

    try:
        process = subprocess.Popen(
            ["opencode", "run", prompt, "--agent", "plan", "--model", model],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout = process.stdout
        if stdout is not None:
            first_char = stdout.read(1)
            if first_char:
                first_token_time = time.time()

        if first_token_time is not None:
            remaining_timeout = timeout - (first_token_time - start_time)
            if remaining_timeout > 0:
                process.wait(timeout=remaining_timeout)
            else:
                process.kill()
                return None
        else:
            process.wait(timeout=timeout)

        if first_token_time:
            return first_token_time - start_time
        return None
    except subprocess.TimeoutExpired:
        if process is not None:
            process.kill()
        return None
    except Exception:
        return None
    finally:
        if process is not None:
            try:
                process.kill()
            except Exception:
                pass


def test_model(model, prompt, iterations, timeout):
    results = []
    for i in range(iterations):
        ttft = measure_ttft(model, prompt, timeout)
        if ttft is not None:
            results.append(ttft)
    return results


def print_progress(model, result):
    if result:
        avg = mean(result)
        print(f"Testing {model} ... {avg:.2f}s")
    else:
        print(f"Testing {model} ... Error")


def print_results(all_results):
    print("\n## Result\n")
    print("| Model              | Average TTFT (s) | Max TTFT (s) |")
    print("| ------------------ | ---------------- | ------------ |")

    sorted_results = sorted(
        all_results.items(), key=lambda x: mean(x[1]) if x[1] else float("inf")
    )

    for model, result in sorted_results:
        if result:
            avg = mean(result)
            max_ttft = max(result)
            print(f"| {model.ljust(18)} | {avg:16.2f} | {max_ttft:12.2f} |")
        else:
            print(f"| {model.ljust(18)} | Error            | Error        |")


def main():
    args = parse_arguments()
    models = get_models_from_providers(args.providers)

    results = {}

    def test_and_progress(model):
        result = test_model(model, args.prompt, args.iterations, args.timeout)
        results[model] = result
        print_progress(model, result)

    with ThreadPoolExecutor() as executor:
        executor.map(test_and_progress, models)

    print_results(all_results=results)


if __name__ == "__main__":
    main()
