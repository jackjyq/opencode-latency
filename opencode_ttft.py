#!/usr/bin/python3

import argparse
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean

DEFAULT_PROMPT = "Explain quantum computing"
DEFAULT_ITERATIONS = 1
DEFAULT_TIMEOUT = 60


def get_models_from_providers(providers):
    models = []
    for provider in providers:
        try:
            result = subprocess.run(
                ["opencode", "models", provider],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                models.extend(result.stdout.strip().split("\n"))
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    return models


def measure_ttft(model, prompt, timeout):
    start_time = time.time()
    first_token_time = None

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
        process.kill()
        return None
    except Exception:
        return None
    finally:
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
        print(f"Testing {model} ... Error", file=sys.stderr)


def print_results(all_results, prompt, providers, models, iterations, timeout):
    print("## Condition\n")
    print("| Argument   | Value                                                    |")
    print("| ---------- | -------------------------------------------------------- |")
    print(
        f"| Providers  | {' '.join(providers) if providers else 'N/A'}                                      |"
    )
    print(f"| Models     | {' '.join(models) if models else 'N/A'} |")
    print(f'| Prompt     | "{prompt}"                              |')
    print(
        f"| Iterations | {iterations}                                                        |"
    )
    print(
        f"| Timeout    | {timeout}                                                       |"
    )

    print("\n## Progress\n")
    for model, result in all_results.items():
        if result:
            avg = mean(result)
            print(f"Testing {model} ... {avg:.2f}s")
        else:
            print(f"Testing {model} ... Error")

    print("\n## Result\n")
    print("| Model              | Average TTFT (s) | Max TTFT (s) |")
    print("| ------------------ | ---------------- | ------------ |")

    sorted_results = sorted(
        all_results.items(), key=lambda x: (mean(x[1]) if x[1] else float("inf"))
    )

    for model, result in sorted_results:
        if result:
            avg = mean(result)
            max_ttft = max(result)
            print(
                f"| {model.ljust(18)} | {avg:.2f}             | {max_ttft:.2f}         |"
            )
        else:
            print(f"| {model.ljust(18)} | Error            | Error        |")


def main():
    parser = argparse.ArgumentParser(description="Measure TTFT of OpenCode models")
    parser.add_argument(
        "--providers", nargs="+", help="Provider IDs to test models from"
    )
    parser.add_argument("--models", nargs="+", help="Specific model IDs to test")
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt to use for testing"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help="Number of iterations per model",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds"
    )

    args = parser.parse_args()

    if not args.providers and not args.models:
        parser.print_help()
        sys.exit(1)

    models_to_test = []
    if args.providers:
        models_to_test.extend(get_models_from_providers(args.providers))
    if args.models:
        models_to_test.extend(args.models)

    if not models_to_test:
        print("No models found to test", file=sys.stderr)
        sys.exit(1)

    results = {}

    def test_and_progress(model):
        result = test_model(model, args.prompt, args.iterations, args.timeout)
        results[model] = result
        print_progress(model, result)

    with ThreadPoolExecutor() as executor:
        executor.map(test_and_progress, models_to_test)

    print_results(
        all_results=results,
        prompt=args.prompt,
        providers=args.providers or [],
        models=models_to_test,
        iterations=args.iterations,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
