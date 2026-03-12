#!/usr/bin/python3

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean


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


def print_condition(providers, models, prompt, iterations, timeout):
    print("## Condition\n")
    print("| Argument   | Value                                                    |")
    print("| ---------- | -------------------------------------------------------- |")
    providers_str = " ".join(providers) if providers else "N/A"
    models_str = " ".join(models) if models else "N/A"
    print(f"| Providers  | {providers_str.ljust(56)} |")
    print(f"| Models     | {models_str.ljust(56)} |")
    print(f'| Prompt     | "{prompt}"'.ljust(56) + " |")
    print(f"| Iterations | {str(iterations).ljust(56)} |")
    print(f"| Timeout    | {str(timeout).ljust(56)} |")
    print("\n## Progress\n")


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
    parser = argparse.ArgumentParser(description="Measure TTFT of OpenCode models")
    parser.add_argument(
        "--providers", nargs="+", help="Provider IDs to test models from"
    )
    parser.add_argument("--models", nargs="+", help="Specific model IDs to test")
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations per model",
    )
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")

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

    print_condition(
        providers=args.providers or [],
        models=models_to_test,
        prompt=args.prompt,
        iterations=args.iterations,
        timeout=args.timeout,
    )

    results = {}

    def test_and_progress(model):
        result = test_model(model, args.prompt, args.iterations, args.timeout)
        results[model] = result
        print_progress(model, result)

    with ThreadPoolExecutor() as executor:
        executor.map(test_and_progress, models_to_test)

    print_results(all_results=results)


if __name__ == "__main__":
    main()
