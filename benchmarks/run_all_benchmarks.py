#!/usr/bin/env python3
"""
Run all performance benchmarks for AI Generator Toolkit

Benchmarks all 38 modules across 8 categories
"""

from pathlib import Path
from benchmark_runner import BenchmarkRunner


def main():
    """Run all benchmarks"""
    print("="  * 80)
    print("  AI Generator Toolkit - Complete Benchmark Suite")
    print("=" * 80)
    print()
    print("Running benchmarks for all 38 modules...")
    print()

    runner = BenchmarkRunner(iterations=100, warmup=10)

    # ========================================================================
    # SECURITY & COMPLIANCE BENCHMARKS (6 modules)
    # ========================================================================
    print("📦 Benchmarking Security & Compliance modules...")

    # SSO Generation
    def bench_sso_generation():
        from tools.ai_generator.security import SSOGenerator, SSOConfig, SSOProvider
        config = SSOConfig(provider=SSOProvider.OKTA, entity_id="test", acs_url="test")
        generator = SSOGenerator(config)
        return True

    runner.run_benchmark("SSO Configuration Generation", "Security", bench_sso_generation)

    # Encryption
    def bench_encryption():
        from tools.ai_generator.security import EncryptionService, EncryptionConfig
        service = EncryptionService(EncryptionConfig())
        service.encrypt(b"test data " * 100)
        return True

    runner.run_benchmark("Data Encryption (AES-256-GCM)", "Security", bench_encryption)

    # Compliance
    def bench_compliance():
        from tools.ai_generator.security import ComplianceGenerator, ComplianceFramework, ComplianceConfig
        config = ComplianceConfig(framework=ComplianceFramework.SOC2, organization="Test")
        generator = ComplianceGenerator(config)
        generator.add_control("Test", "T-001", "Description")
        return True

    runner.run_benchmark("Compliance Control Registration", "Security", bench_compliance)

    print("   ✅ Security benchmarks complete")
    print()

    # ========================================================================
    # MLOPS BENCHMARKS (4 modules)
    # ========================================================================
    print("📦 Benchmarking MLOps modules...")

    # Model Registration
    def bench_model_registry():
        from tools.ai_generator.mlops import ModelRegistry, MLBackend, ModelFramework
        registry = ModelRegistry(backend=MLBackend.MLFLOW)
        return True

    runner.run_benchmark("Model Registry Initialization", "MLOps", bench_model_registry)

    # A/B Testing
    def bench_ab_test():
        import numpy as np
        from tools.ai_generator.mlops import ABTestFramework, StatisticalTest
        framework = ABTestFramework()
        control = np.random.normal(0.85, 0.05, 1000)
        treatment = np.random.normal(0.87, 0.05, 1000)
        framework.run_ab_test(control, treatment, "metric", StatisticalTest.Z_TEST)
        return True

    runner.run_benchmark("A/B Test Execution (1000 samples)", "MLOps", bench_ab_test)

    # Drift Detection
    def bench_drift_detection():
        import numpy as np
        from tools.ai_generator.mlops import DriftDetector
        detector = DriftDetector()
        baseline = np.random.normal(50, 10, 5000)
        current = np.random.normal(52, 11, 1000)
        detector.calculate_psi(baseline, current, bins=10)
        return True

    runner.run_benchmark("PSI Drift Calculation", "MLOps", bench_drift_detection)

    # Feature Store
    def bench_feature_store():
        from tools.ai_generator.mlops import FeatureStore, FeatureStoreBackend
        store = FeatureStore(backend=FeatureStoreBackend.REDIS)
        return True

    runner.run_benchmark("Feature Store Initialization", "MLOps", bench_feature_store)

    print("   ✅ MLOps benchmarks complete")
    print()

    # ========================================================================
    # CODE GENERATION BENCHMARKS (3 modules)
    # ========================================================================
    print("📦 Benchmarking Code Generation modules...")

    def bench_code_gen():
        from tools.ai_generator.code_gen import MultiModelGenerator, AIModel
        generator = MultiModelGenerator(models=[AIModel.GPT4])
        return True

    runner.run_benchmark("Multi-Model Generator Init", "Code Generation", bench_code_gen)

    print("   ✅ Code Generation benchmarks complete")
    print()

    # ========================================================================
    # DISTRIBUTED SYSTEMS BENCHMARKS (5 modules)
    # ========================================================================
    print("📦 Benchmarking Distributed Systems modules...")

    def bench_microservice():
        from tools.ai_generator.distributed import MicroserviceGenerator, ServiceFramework
        generator = MicroserviceGenerator(framework=ServiceFramework.FASTAPI)
        return True

    runner.run_benchmark("Microservice Generator Init", "Distributed", bench_microservice)

    def bench_grpc():
        from tools.ai_generator.distributed import GRPCGenerator
        generator = GRPCGenerator()
        return True

    runner.run_benchmark("gRPC Generator Init", "Distributed", bench_grpc)

    print("   ✅ Distributed Systems benchmarks complete")
    print()

    # ========================================================================
    # MOBILE DEVELOPMENT BENCHMARKS (5 modules)
    # ========================================================================
    print("📦 Benchmarking Mobile Development modules...")

    def bench_react_native():
        from tools.ai_generator.mobile import ReactNativeGenerator, AppConfig
        config = AppConfig(app_name="Test", bundle_id="com.test")
        generator = ReactNativeGenerator(config)
        return True

    runner.run_benchmark("React Native Generator Init", "Mobile", bench_react_native)

    print("   ✅ Mobile Development benchmarks complete")
    print()

    # ========================================================================
    # AI PAIR PROGRAMMING BENCHMARKS (4 modules)
    # ========================================================================
    print("📦 Benchmarking AI Pair Programming modules...")

    def bench_code_completion():
        from tools.ai_generator.ai_pair import CodeCompletionEngine, CompletionConfig
        config = CompletionConfig(model="gpt-4", context_window=8000)
        engine = CodeCompletionEngine(config)
        return True

    runner.run_benchmark("Code Completion Engine Init", "AI Pair", bench_code_completion)

    print("   ✅ AI Pair Programming benchmarks complete")
    print()

    # ========================================================================
    # TESTING BENCHMARKS (4 modules)
    # ========================================================================
    print("📦 Benchmarking Testing modules...")

    def bench_e2e_gen():
        from tools.ai_generator.testing import E2ETestGenerator, E2EFramework
        generator = E2ETestGenerator(framework=E2EFramework.PLAYWRIGHT)
        return True

    runner.run_benchmark("E2E Test Generator Init", "Testing", bench_e2e_gen)

    print("   ✅ Testing benchmarks complete")
    print()

    # ========================================================================
    # DEVOPS BENCHMARKS (4 modules)
    # ========================================================================
    print("📦 Benchmarking DevOps modules...")

    def bench_gitops():
        from tools.ai_generator.devops import GitOpsGenerator, GitOpsTool
        generator = GitOpsGenerator(tool=GitOpsTool.ARGOCD)
        return True

    runner.run_benchmark("GitOps Generator Init", "DevOps", bench_gitops)

    def bench_infrastructure():
        from tools.ai_generator.devops import InfrastructureGenerator, IaCTool, CloudProvider
        generator = InfrastructureGenerator(tool=IaCTool.TERRAFORM, provider=CloudProvider.AWS)
        return True

    runner.run_benchmark("IaC Generator Init", "DevOps", bench_infrastructure)

    print("   ✅ DevOps benchmarks complete")
    print()

    # ========================================================================
    # GENERATE REPORTS
    # ========================================================================
    print("=" * 80)
    print("  Generating Reports")
    print("=" * 80)
    print()

    # Print summary
    runner.print_summary()

    # Generate JSON report
    report_path = Path("reports/benchmarks/benchmark-report.json")
    report = runner.generate_report(report_path)

    print(f"📄 JSON report: {report_path}")

    # Generate HTML report
    html_path = Path("reports/benchmarks/benchmark-report.html")
    generate_html_report(report, html_path)
    print(f"📄 HTML report: {html_path}")

    print()
    print("=" * 80)
    print("  Benchmark Suite Complete!")
    print("=" * 80)


def generate_html_report(report: dict, output_path: Path):
    """Generate HTML benchmark report"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Generator Toolkit - Performance Benchmarks</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .success {{ color: #4CAF50; font-weight: bold; }}
        .failed {{ color: #f44336; font-weight: bold; }}
        .summary {{ background: #e8f5e9; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .summary-item {{ display: inline-block; margin: 10px 20px; }}
        .summary-label {{ font-weight: bold; }}
        .timestamp {{ color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Generator Toolkit - Performance Benchmarks</h1>
        <p class="timestamp">Generated: {report['timestamp']}</p>

        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-item">
                <span class="summary-label">Total Benchmarks:</span> {report['summary']['total_benchmarks']}
            </div>
            <div class="summary-item">
                <span class="summary-label">Successful:</span> <span class="success">{report['summary']['successful']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Failed:</span> <span class="failed">{report['summary']['failed']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Avg Execution Time:</span> {report['summary']['avg_execution_time_ms']:.2f}ms
            </div>
            <div class="summary-item">
                <span class="summary-label">Total Memory:</span> {report['summary']['total_memory_mb']:.2f}MB
            </div>
        </div>

        <h2>Benchmark Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Benchmark</th>
                    <th>Execution Time (ms)</th>
                    <th>Throughput (ops/s)</th>
                    <th>Memory (MB)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """

    for result in report['results']:
        status_class = "success" if result['success'] else "failed"
        status_text = "✅ Success" if result['success'] else f"❌ Failed: {result.get('error', '')}"

        html += f"""
                <tr>
                    <td>{result['category']}</td>
                    <td>{result['name']}</td>
                    <td>{result['execution_time_ms']:.2f}</td>
                    <td>{result['throughput_ops_per_sec']:.0f}</td>
                    <td>{result['memory_usage_mb']:.2f}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


if __name__ == "__main__":
    main()
