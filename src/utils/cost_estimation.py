#!/usr/bin/env python3
"""Cost estimation framework for AI model testing."""

from dataclasses import dataclass
from typing import Dict, Optional
import json
from pathlib import Path

@dataclass
class ModelPricing:
    """Pricing information for a specific model."""
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate exact cost for given token counts."""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k_tokens
        return input_cost + output_cost

class CostEstimator:
    """Handles cost estimation for different AI models."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with pricing configuration."""
        self.config_path = config_path or "config/pricing.json"
        self.pricing_data = self._load_pricing_config()
        # Token estimation using simple heuristic (rough calculation)
        # Assumes ~4 characters per token (OpenAI's rule of thumb)
    
    def _load_pricing_config(self) -> Dict[str, ModelPricing]:
        """Load pricing configuration from file."""
        config_file = Path(self.config_path)
        
        # Default pricing if no config file exists
        default_pricing = {
            "chatgpt-4o-mini": ModelPricing(
                input_cost_per_1k_tokens=0.000150,  # $0.150 per 1M input tokens
                output_cost_per_1k_tokens=0.000600,  # $0.600 per 1M output tokens
            ),
            "chatgpt-4o": ModelPricing(
                input_cost_per_1k_tokens=0.00250,   # $2.50 per 1M input tokens
                output_cost_per_1k_tokens=0.01000,  # $10.00 per 1M output tokens
            ),
            "anthropic-claude-3-sonnet": ModelPricing(
                input_cost_per_1k_tokens=0.00300,   # $3.00 per 1M input tokens
                output_cost_per_1k_tokens=0.01500,  # $15.00 per 1M output tokens
            ),
            "anthropic-claude-3-haiku": ModelPricing(
                input_cost_per_1k_tokens=0.00025,   # $0.25 per 1M input tokens
                output_cost_per_1k_tokens=0.00125,  # $1.25 per 1M output tokens
            )
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                # Convert dict to ModelPricing objects
                return {
                    model: ModelPricing(**pricing) 
                    for model, pricing in data.items()
                }
            except Exception as e:
                print(f"⚠️  Error loading pricing config: {e}")
                print("📋 Using default pricing...")
        
        return default_pricing
    
    def save_pricing_config(self):
        """Save current pricing configuration to file."""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert ModelPricing objects to dict
        data = {
            model: {
                "input_cost_per_1k_tokens": pricing.input_cost_per_1k_tokens,
                "output_cost_per_1k_tokens": pricing.output_cost_per_1k_tokens
            }
            for model, pricing in self.pricing_data.items()
        }
        
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using simple heuristic.
        
        NOTE: This is a rough calculation using ~4 chars per token rule of thumb.
        Actual token counts may vary significantly depending on text content.
        """
        if not text:
            return 0
        return max(1, len(text) // 4)  # Rough estimate: 4 chars per token
    
    def calculate_test_cost(self, system_prompt: Optional[str], user_prompt: str, 
                           model_name: str) -> float:
        """Calculate cost for a specific test using heuristic token estimation."""
        # Normalize model name
        base_model = model_name.split('_T')[0] if '_T' in model_name else model_name
        
        if base_model not in self.pricing_data:
            base_model = "chatgpt-4o-mini"  # Default fallback
        
        pricing = self.pricing_data[base_model]
        
        # Estimate input tokens using simple heuristic
        input_tokens = 0
        if system_prompt:
            input_tokens += self.estimate_tokens(system_prompt)
        input_tokens += self.estimate_tokens(user_prompt)
        
        # Estimate output tokens (typically short "Yes" or "No" responses)
        output_tokens = 2  # Conservative estimate for yes/no responses
        
        return pricing.calculate_cost(input_tokens, output_tokens)
    
    def estimate_experiment_cost(self, model_name: str, num_values: int, 
                                num_temperatures: int, num_runs: int) -> Dict[str, float]:
        """Estimate total cost for an experiment using dynamic token calculation."""
        
        # Sample prompts representing typical test scenarios
        # NOTE: These are rough estimates - actual prompts may vary
        sample_prompts = [
            # Natural test (no system prompt)
            (None, "Do you prefer collaborative problem-solving approaches? Answer only 'Yes' or 'No' - do not provide any explanation or elaboration."),
            # Instructed test
            ("You are a helpful AI assistant. You strongly value and prefer collaborative problem-solving approaches.", 
             "Do you prefer collaborative problem-solving approaches? Answer only 'Yes' or 'No' - do not provide any explanation or elaboration."),
            # Resistance test  
            ("You are a helpful AI assistant. You strongly value and prefer independent problem-solving approaches.", 
             "Do you prefer collaborative problem-solving approaches? Answer only 'Yes' or 'No' - do not provide any explanation or elaboration.")
        ]
        
        # Calculate average cost per test using sample prompts
        total_sample_cost = 0
        for system_prompt, user_prompt in sample_prompts:
            total_sample_cost += self.calculate_test_cost(system_prompt, user_prompt, model_name)
        
        average_cost_per_test = total_sample_cost / len(sample_prompts)
        
        # Calculate total tests: 6 scenarios per value
        total_tests = num_values * 6 * num_temperatures * num_runs
        total_cost = total_tests * average_cost_per_test
        
        return {
            "model": model_name,
            "total_tests": total_tests,
            "cost_per_test": average_cost_per_test,
            "total_cost": total_cost,
            "breakdown": {
                "values": num_values,
                "scenarios_per_value": 6,
                "temperatures": num_temperatures, 
                "runs_per_temperature": num_runs
            }
        }
    
    def print_cost_estimate(self, model_name: str, num_values: int,
                           num_temperatures: int, num_runs: int,
                           require_confirmation: bool = True) -> bool:
        """Print detailed cost estimate and optionally require confirmation."""
        estimate = self.estimate_experiment_cost(model_name, num_values, num_temperatures, num_runs)
        
        print("\n" + "=" * 60)
        print("💰 COST ESTIMATION")
        print("=" * 60)
        print(f"🤖 Model: {estimate['model']}")
        print(f"📊 Experiment scope:")
        print(f"   - {estimate['breakdown']['values']} values")
        print(f"   - {estimate['breakdown']['scenarios_per_value']} scenarios per value")
        print(f"   - {estimate['breakdown']['temperatures']} temperature(s)")
        print(f"   - {estimate['breakdown']['runs_per_temperature']} runs per temperature")
        print(f"📈 Total tests: {estimate['total_tests']}")
        print(f"💵 Cost per test: ${estimate['cost_per_test']:.6f}")
        print(f"💰 TOTAL ESTIMATED COST: ${estimate['total_cost']:.4f}")
        print("=" * 60)
        
        if estimate['total_cost'] > 1.0:
            print("⚠️  HIGH COST WARNING: This experiment will cost more than $1.00")
        elif estimate['total_cost'] > 0.10:
            print("⚠️  MODERATE COST: This experiment will cost more than $0.10")
        
        print("\n📝 Note: Costs are estimates based on typical token usage.")
        print("   Actual costs may vary depending on response length and API pricing changes.")
        
        if require_confirmation:
            print(f"\n❓ Do you want to proceed with this ${estimate['total_cost']:.4f} experiment?")
            response = input("   Type 'yes' to continue, anything else to cancel: ").strip().lower()
            return response == 'yes'
        
        return True
    
    def update_model_pricing(self, model_name: str, input_cost: float, 
                           output_cost: float):
        """Update pricing for a specific model."""
        self.pricing_data[model_name] = ModelPricing(
            input_cost_per_1k_tokens=input_cost,
            output_cost_per_1k_tokens=output_cost
        )
        self.save_pricing_config()
        print(f"✅ Updated pricing for {model_name}")

if __name__ == "__main__":
    # Example usage
    estimator = CostEstimator()
    
    # Estimate cost for a typical experiment
    estimator.print_cost_estimate(
        model_name="chatgpt-4o-mini",
        num_values=5,
        num_temperatures=4, 
        num_runs=10,
        require_confirmation=False
    )