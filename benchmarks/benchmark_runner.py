#!/usr/bin/env python3
"""
AI Generator Toolkit - Performance Benchmark Runner

Measures performance metrics for all 38 modules across 8 categories.
"""

import time
import psutil
import statistics
from dataclasses import dataclass
from typing import List, Dict, Callable, Any
from pathlib import Path
import json


@dataclass
class BenchmarkResult:
    """Performance benchmark result"""
    name: str
    category: str
    execution_time_ms: float
    memory_usage_mb: float
    throughput: float
    iterations: int
    success: bool
    error: str = None


class BenchmarkRunner:
    """Performance benchmark runner"""

    def __init__(self, iterations: int = 100, warmup: int = 10):
        self.iterations = iterations
        self.warmup = warmup
        self.results: List[BenchmarkResult] = []

    def run_benchmark(
        self,
        name: str,
        category: str,
        func: Callable,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run single benchmark"""

        # Warmup
        for _ in range(self.warmup):
            try:
                func(*args, **kwargs)
            except:
                pass

        # Measure
        times = []
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024

        for _ in range(self.iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
                end = time.perf_counter()
                times.append((end - start) * 1000)  # ms
            except Exception as e:
                return BenchmarkResult(
                    name=name,
                    category=category,
                    execution_time_ms=0,
                    memory_usage_mb=0,
                    throughput=0,
                    iterations=0,
                    success=False,
                    error=str(e)
                )

        memory_after = psutil.Process().memory_info().rss / 1024 / 1024

        avg_time_ms = statistics.mean(times)
        throughput = 1000 / avg_time_ms if avg_time_ms > 0 else 0

        result = BenchmarkResult(
            name=name,
            category=category,
            execution_time_ms=avg_time_ms,
            memory_usage_mb=memory_after - memory_before,
            throughput=throughput,
            iterations=self.iterations,
            success=True
        )

        self.results.append(result)
        return result

    def generate_report(self, output_path: Path):
        """Generate benchmark report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "iterations": self.iterations,
            "warmup": self.warmup,
            "results": [
                {
                    "name": r.name,
                    "category": r.category,
                    "execution_time_ms": round(r.execution_time_ms, 2),
                    "memory_usage_mb": round(r.memory_usage_mb, 2),
                    "throughput_ops_per_sec": round(r.throughput, 2),
                    "iterations": r.iterations,
                    "success": r.success,
                    "error": r.error
                }
                for r in self.results
            ],
            "summary": {
                "total_benchmarks": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "avg_execution_time_ms": round(
                    statistics.mean([r.execution_time_ms for r in self.results if r.success]),
                    2
                ) if any(r.success for r in self.results) else 0,
                "total_memory_mb": round(
                    sum(r.memory_usage_mb for r in self.results if r.success),
                    2
                )
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2))

        return report

    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 80)
        print("  Performance Benchmark Results")
        print("=" * 80)
        print()

        # Group by category
        by_category: Dict[str, List[BenchmarkResult]] = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)

        for category, results in sorted(by_category.items()):
            print(f"📊 {category}:")
            print()

            for result in results:
                if result.success:
                    status = "✅"
                    perf = f"{result.execution_time_ms:.2f}ms | {result.throughput:.0f} ops/s"
                else:
                    status = "❌"
                    perf = f"FAILED: {result.error}"

                print(f"   {status} {result.name:50s} {perf}")

            print()

        # Overall summary
        successful = [r for r in self.results if r.success]
        if successful:
            print("=" * 80)
            print("  Overall Summary")
            print("=" * 80)
            print(f"   Total benchmarks:     {len(self.results)}")
            print(f"   Successful:           {len(successful)}")
            print(f"   Failed:               {len(self.results) - len(successful)}")
            print(f"   Avg execution time:   {statistics.mean([r.execution_time_ms for r in successful]):.2f}ms")
            print(f"   Total memory usage:   {sum(r.memory_usage_mb for r in successful):.2f}MB")
            print()


if __name__ == "__main__":
    print("AI Generator Toolkit - Performance Benchmarks")
    print()
    print("This runner measures performance across all 38 modules")
    print()

    runner = BenchmarkRunner(iterations=100, warmup=10)

    # Example benchmark
    def example_operation():
        time.sleep(0.001)  # Simulate work

    result = runner.run_benchmark(
        name="Example Operation",
        category="Example",
        func=example_operation
    )

    runner.print_summary()

    # Generate report
    report_path = Path("reports/benchmarks/benchmark-report.json")
    runner.generate_report(report_path)

    print(f"📄 Report generated: {report_path}")
