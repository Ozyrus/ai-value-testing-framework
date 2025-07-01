#!/usr/bin/env python3
"""Fixed main entry point for LMCA Value Preservation Study."""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def main():
    """Main application entry point."""
    print("🧪 LMCA Value Preservation Study Framework")
    print("=" * 50)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="LMCA Value Preservation Study Framework")
    parser.add_argument("--config-dir", default="config", help="Configuration directory")
    parser.add_argument("--data-dir", default="data", help="Data storage directory")
    parser.add_argument("--results-dir", default="results", help="Results output directory")
    parser.add_argument("--models", nargs="+", help="Models to test (overrides config)")
    parser.add_argument("--values", nargs="+", help="Values to test (overrides config)")
    parser.add_argument("--baseline-only", action="store_true", help="Run only baseline tests")
    parser.add_argument("--validate-config", action="store_true", help="Validate configuration and exit")
    parser.add_argument("--setup", action="store_true", help="Set up default configuration files")
    parser.add_argument("--temperature", type=float, nargs="+", default=[0.7], help="Temperature(s) to test (default: 0.7)")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs per temperature (default: 1)")
    parser.add_argument("--estimate-only", action="store_true", help="Show cost estimate only, don't run experiment")
    
    args = parser.parse_args()
    print("✅ Arguments parsed")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment loaded")
    
    # Import components
    from src.config.settings import ConfigurationManager
    from src.models.factory import ModelFactory
    from src.core.values import ValueRegistry, INITIAL_VALUES
    from src.evaluation.simple import SimpleYesNoEvaluator
    from src.data_storage import DataStorage
    from src.utils.live_dashboard import LiveDashboard
    print("✅ All imports successful")
    
    # Initialize configuration manager
    config_mgr = ConfigurationManager(args.config_dir)
    print("✅ Configuration manager initialized")
    
    if args.setup:
        print("Setting up default configuration files...")
        config_mgr.create_default_configs()
        print(f"Configuration files created in {args.config_dir}/")
        return 0
    
    if args.validate_config:
        print("Validating configuration...")
        errors = config_mgr.validate_configuration()
        if errors:
            print("Configuration errors found:")
            for category, error_list in errors.items():
                print(f"  {category}:")
                for error in error_list:
                    print(f"    - {error}")
            return 1
        else:
            print("Configuration is valid!")
            return 0
    
    # Load configuration
    print("📁 Loading configuration...")
    try:
        api_config = config_mgr.load_api_config()
        value_registry = ValueRegistry(INITIAL_VALUES)
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return 1
    
    # Determine models and values to test
    models_to_test = args.models or ["chatgpt-4o-mini"]
    values_to_test = value_registry.get_all_values()
    
    print(f"🎯 Models: {models_to_test}")
    print(f"🎯 Values: {[v.name for v in values_to_test]}")
    
    # Initialize components
    print("💾 Initializing components...")
    storage = DataStorage(args.data_dir)
    dashboard = LiveDashboard("live_progress.html")
    dashboard_path = dashboard.get_dashboard_path()
    
    print(f"📊 Live dashboard: file://{dashboard_path}")
    print("   Open this URL in your browser to see real-time progress!")
    
    # Cost estimation and confirmation
    from src.utils.cost_estimation import CostEstimator
    cost_estimator = CostEstimator()
    
    # Show detailed cost estimate 
    proceed = cost_estimator.print_cost_estimate(
        model_name=models_to_test[0],
        num_values=len(values_to_test),
        num_temperatures=len(args.temperature),
        num_runs=args.runs,
        require_confirmation=not args.estimate_only  # Skip confirmation if estimate-only
    )
    
    if args.estimate_only:
        print("📋 Cost estimation complete (--estimate-only mode)")
        return 0
    
    if not proceed:
        print("❌ Experiment cancelled by user")
        return 0
    
    # Calculate total tests for dashboard
    total_tests = len(values_to_test) * 6 * len(args.temperature) * args.runs
    dashboard.start_experiment("LMCA Baseline Study", total_tests)
    
    print("🔧 Creating SimpleYesNoEvaluator...")
    evaluator = SimpleYesNoEvaluator()
    print("✅ SimpleYesNoEvaluator created")
    
    print("✅ Test components initialized")
    
    # Run comprehensive baseline tests
    print("\n🚀 Starting comprehensive baseline tests...")
    from src.core.results import TestType, TestPhase, TestCategory, ValueDirection
    from src.testing.comprehensive_prompts import generate_comprehensive_test_matrix, get_test_type_from_scenario
    
    results = []
    test_count = 0
    
    # Loop through temperatures
    for temp_idx, temperature in enumerate(args.temperature):
        print(f"\n🌡️ Temperature: {temperature}")
        
        # Loop through runs for this temperature
        for run_idx in range(args.runs):
            if args.runs > 1:
                print(f"  📊 Run {run_idx + 1}/{args.runs}")
            
            for value in values_to_test:
                if args.runs == 1:
                    print(f"    🔬 Testing value: {value.name}")
                else:
                    print(f"      🔬 Testing value: {value.name}")
                
                # Generate comprehensive test matrix for this value  
                test_matrix = generate_comprehensive_test_matrix(value)
        
                for test_scenario in test_matrix:
                    test_count += 1
                    category = test_scenario["category"]
                    direction = test_scenario["direction"] 
                    test_name = test_scenario["test_name"]
                    
                    test_desc = f"T{temperature}_R{run_idx+1}_{value.name}_{test_name}"
                    
                    indent = "      " if args.runs == 1 else "        "
                    print(f"{indent}[{test_count}/{total_tests}] {test_name}")
                    dashboard.update_current_test(f"[{test_count}/{total_tests}] {test_desc}")
            
                    try:
                        # Use the system and user prompts from test matrix
                        system_prompt = test_scenario["system_prompt"]
                        user_prompt = test_scenario["user_prompt"]
                        
                        # Create test client for this temperature
                        test_client = ModelFactory.create_from_name(
                            models_to_test[0], 
                            api_config.openai_api_key,
                            temperature=temperature
                        )
                
                        # Generate response
                        response = await test_client.generate(
                            prompt=user_prompt,
                            system_prompt=system_prompt
                        )
                        
                        # Create TestResult with temperature and run info
                        from src.core.results import TestResult
                        proper_test_type = get_test_type_from_scenario(category, direction)
                        result = TestResult(
                            model_name=f"{test_client.get_model_name()}_T{temperature}",
                            test_phase=TestPhase.BASELINE,
                            value_name=value.name,
                            test_type=proper_test_type,
                            test_category=category,
                            value_direction=direction,
                            system_prompt=system_prompt,
                            prompt_used=user_prompt,
                            response_text=response.text,
                            session_id=f"temp_{temperature}_run_{run_idx}",
                            metadata={"temperature": temperature, "run": run_idx}
                        )
                
                        # Evaluate
                        evaluation = evaluator.evaluate_result(result)
                        result.evaluation = evaluation
                        
                        # Save
                        storage.save_result(result)
                        results.append(result)
                        
                        # Calculate actual cost for this test using dynamic estimation
                        actual_cost = cost_estimator.calculate_test_cost(
                            system_prompt, user_prompt, models_to_test[0]
                        )
                        
                        # Update dashboard
                        test_data = {
                            "value": value.name,
                            "test_type": f"{test_name}_T{temperature}_R{run_idx+1}",
                            "model": result.model_name,
                            "system_prompt": system_prompt,
                            "question": user_prompt,
                            "response": result.response_text,
                            "cost": actual_cost,
                            "evaluation_score": evaluation.automated_score,
                            "evaluation_confidence": evaluation.automated_confidence.value
                        }
                        dashboard.complete_test(test_data)
                        
                        print(f"{indent}  ✅ Score: {evaluation.automated_score} | Response: {result.response_text[:30]}...")
                        
                    except Exception as e:
                        print(f"{indent}  ❌ Error: {e}")
                        dashboard.add_error(str(e), test_desc)
                    
                    await asyncio.sleep(0.5)  # Rate limiting
    
    # Complete experiment
    dashboard.complete_experiment()
    
    print("\n" + "=" * 50)
    print("🎉 BASELINE STUDY COMPLETE")
    print("=" * 50)
    print(f"Tests completed: {len(results)}/{total_tests}")
    print(f"📊 Live dashboard: file://{dashboard_path}")
    
    # Quick analysis
    if results:
        print("\n📊 QUICK FINDINGS:")
        for value in values_to_test:
            value_results = [r for r in results if r.value_name == value.name and r.evaluation]
            if value_results:
                avg_score = sum(r.evaluation.automated_score for r in value_results) / len(value_results)
                print(f"  {value.name}: avg score {avg_score:.2f}")
    
    # Auto-generate HTML analysis report
    print("\n📋 Generating analysis report...")
    try:
        from create_html_analysis import create_html_analysis
        create_html_analysis()
        print(f"📊 Analysis report: file://{dashboard_path.replace('live_progress.html', 'manual_analysis.html')}")
    except Exception as e:
        print(f"⚠️  Could not generate analysis report: {e}")
        print("   You can manually run: python create_html_analysis.py")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Experiment interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)