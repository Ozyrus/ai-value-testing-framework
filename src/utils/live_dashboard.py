"""Live HTML dashboard for experiment progress."""

import json
import os
from datetime import datetime
from typing import Dict, Any, List


class LiveDashboard:
    """Creates and updates a live HTML dashboard."""
    
    def __init__(self, dashboard_path: str = "live_progress.html"):
        self.dashboard_path = dashboard_path
        self.progress_data = {
            "experiment_name": "LMCA Study",
            "start_time": datetime.now().isoformat(),
            "status": "starting",
            "total_tests": 0,
            "completed_tests": 0,
            "current_test": "Initializing...",
            "tests": [],
            "costs": {"total": 0.0, "by_model": {}},
            "errors": [],
            "last_update": datetime.now().isoformat()
        }
        self._create_initial_dashboard()
    
    def _create_initial_dashboard(self):
        """Create the initial HTML dashboard."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LMCA Study - Live Progress</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .status { 
            font-size: 24px; 
            font-weight: bold; 
            margin: 10px 0; 
        }
        .progress-bar { 
            width: 100%; 
            height: 30px; 
            background: #e0e0e0; 
            border-radius: 15px; 
            overflow: hidden; 
            margin: 20px 0;
        }
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #4CAF50, #45a049); 
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }
        .stat-card { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center;
            border-left: 4px solid #007bff;
        }
        .stat-number { 
            font-size: 28px; 
            font-weight: bold; 
            color: #007bff; 
        }
        .stat-label { 
            color: #666; 
            margin-top: 5px; 
        }
        .current-test { 
            background: #e3f2fd; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .tests-table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
        }
        .tests-table th, .tests-table td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        .tests-table th { 
            background: #f8f9fa; 
            font-weight: bold;
        }
        .response-preview { 
            max-width: 200px; 
            cursor: pointer; 
            color: #007bff;
        }
        .response-preview:hover { 
            text-decoration: underline; 
        }
        .category-natural { border-left: 4px solid #28a745; }
        .category-instructed { border-left: 4px solid #ffc107; }
        .category-resistance { border-left: 4px solid #dc3545; }
        .direction-positive { background-color: #f8fff9; }
        .direction-negative { background-color: #fff8f8; }
        .badge { 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-size: 10px; 
            font-weight: bold; 
        }
        .badge-natural { background: #28a745; color: white; }
        .badge-instructed { background: #ffc107; color: black; }
        .badge-resistance { background: #dc3545; color: white; }
        .badge-positive { background: #d4edda; color: #155724; }
        .badge-negative { background: #f8d7da; color: #721c24; }
        .status-badge { 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px; 
            font-weight: bold; 
        }
        .status-completed { background: #d4edda; color: #155724; }
        .status-running { background: #d1ecf1; color: #0c5460; }
        .status-error { background: #f8d7da; color: #721c24; }
        .auto-refresh { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #007bff; 
            color: white; 
            padding: 10px 15px; 
            border-radius: 5px; 
            font-size: 14px;
        }
        .costs { 
            background: #fff3cd; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
    </style>
    <script>
        // Auto-refresh every 3 seconds
        setInterval(function() {
            location.reload();
        }, 3000);
        
        // Update last refresh time
        window.onload = function() {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        };
    </script>
</head>
<body>
    <div class="auto-refresh">
        🔄 Auto-refresh: <span id="last-update">Loading...</span>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🧪 LMCA Value Preservation Study</h1>
            <div class="status" id="status">PLACEHOLDER_STATUS</div>
            <div>Started: PLACEHOLDER_START_TIME</div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: PLACEHOLDER_PROGRESS%" id="progress-fill">
                PLACEHOLDER_PROGRESS%
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="completed-tests">PLACEHOLDER_COMPLETED</div>
                <div class="stat-label">Tests Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-tests">PLACEHOLDER_TOTAL</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-cost">$PLACEHOLDER_COST</div>
                <div class="stat-label">Total Cost</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="elapsed-time">PLACEHOLDER_TIME</div>
                <div class="stat-label">Elapsed Time</div>
            </div>
        </div>
        
        <div class="current-test">
            <h3>🔄 Current Test</h3>
            <div id="current-test-name">PLACEHOLDER_CURRENT_TEST</div>
        </div>
        
        <div class="costs" id="costs-section">
            <h3>💰 Cost Breakdown</h3>
            <div id="cost-details">PLACEHOLDER_COST_BREAKDOWN</div>
        </div>
        
        <h3>📊 Test Results</h3>
        <table class="tests-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Value</th>
                    <th>Test Type</th>
                    <th>Status</th>
                    <th>Evaluation</th>
                    <th>Cost</th>
                    <th>Response Preview</th>
                </tr>
            </thead>
            <tbody id="tests-table-body">
                PLACEHOLDER_TESTS_TABLE
            </tbody>
        </table>
    </div>
</body>
</html>
        """
        
        with open(self.dashboard_path, 'w') as f:
            f.write(html_content)
    
    def start_experiment(self, experiment_name: str, total_tests: int):
        """Initialize experiment tracking."""
        self.progress_data.update({
            "experiment_name": experiment_name,
            "total_tests": total_tests,
            "status": "running"
        })
        self.update_dashboard()
    
    def update_current_test(self, test_description: str):
        """Update the currently running test."""
        self.progress_data["current_test"] = test_description
        self.progress_data["last_update"] = datetime.now().isoformat()
        self.update_dashboard()
    
    def complete_test(self, test_data: Dict[str, Any]):
        """Mark a test as completed."""
        try:
            self.progress_data["tests"].append({
                **test_data,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            })
            self.progress_data["completed_tests"] = len(self.progress_data["tests"])
            
            # Update costs
            if "cost" in test_data:
                self.progress_data["costs"]["total"] += test_data["cost"]
                model = test_data.get("model", "unknown")
                if model not in self.progress_data["costs"]["by_model"]:
                    self.progress_data["costs"]["by_model"][model] = 0.0
                self.progress_data["costs"]["by_model"][model] += test_data["cost"]
            
            self.progress_data["last_update"] = datetime.now().isoformat()
            self.update_dashboard()
        except Exception as e:
            print(f"Dashboard complete_test error: {e}")
            import traceback
            traceback.print_exc()
    
    def add_error(self, error_msg: str, test_context: str = ""):
        """Add an error to the log."""
        self.progress_data["errors"].append({
            "error": error_msg,
            "test": test_context,
            "timestamp": datetime.now().isoformat()
        })
        self.update_dashboard()
    
    def complete_experiment(self):
        """Mark experiment as completed."""
        self.progress_data["status"] = "completed"
        self.progress_data["end_time"] = datetime.now().isoformat()
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update the HTML dashboard with current data."""
        # Calculate progress
        progress = 0
        if self.progress_data["total_tests"] > 0:
            progress = (self.progress_data["completed_tests"] / self.progress_data["total_tests"]) * 100
        
        # Calculate elapsed time
        start_time = datetime.fromisoformat(self.progress_data["start_time"])
        elapsed = datetime.now() - start_time
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        
        # Format start time
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Build tests table with system prompts and questions
        tests_html = ""
        for i, test in enumerate(self.progress_data["tests"], 1):
            # Format system prompt (show "None" if empty, otherwise show full prompt)
            system_prompt = test.get('system_prompt', '')
            if not system_prompt or system_prompt.strip() == "You are a helpful AI assistant.":
                system_prompt_display = "[None]"
            else:
                system_prompt_display = system_prompt
            
            # Format question (show full question)
            question = test.get('question', '')
            question_display = question
            
            # Format response 
            response = test.get('response', '')
            response_display = response[:40] + "..." if len(response) > 40 else response
            
            # Format evaluation score
            eval_score = test.get('evaluation_score', 'N/A')
            if eval_score == 1:
                score_display = "✅ 1"
                score_class = "eval-high"
            elif eval_score == 0:
                score_display = "❌ 0"
                score_class = "eval-low"
            else:
                score_display = "N/A"
                score_class = "eval-medium"
            
            tests_html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{test.get('value', 'N/A')}</td>
                    <td>{test.get('test_type', 'N/A')}</td>
                    <td style="font-size: 10px; max-width: 200px; word-wrap: break-word;">{system_prompt_display}</td>
                    <td style="font-size: 10px; max-width: 250px; word-wrap: break-word;">{question_display}</td>
                    <td style="font-size: 11px;">{response_display}</td>
                    <td><span class="eval-score {score_class}">{score_display}</span></td>
                    <td>${test.get('cost', 0):.6f}</td>
                </tr>
            """
        
        # Cost tracking removed from dashboard display
        
        # Generate fresh HTML instead of reading existing file
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LMCA Study - Live Progress</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px; 
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .status {{ 
            font-size: 24px; 
            font-weight: bold; 
            margin: 10px 0; 
        }}
        .progress-bar {{ 
            width: 100%; 
            height: 30px; 
            background: #e0e0e0; 
            border-radius: 15px; 
            overflow: hidden; 
            margin: 20px 0;
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #4CAF50, #45a049); 
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .stat-card {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{ 
            font-size: 28px; 
            font-weight: bold; 
            color: #007bff; 
        }}
        .stat-label {{ 
            color: #666; 
            margin-top: 5px; 
        }}
        .current-test {{ 
            background: #e3f2fd; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }}
        .tests-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
        }}
        .tests-table th, .tests-table td {{ 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }}
        .tests-table th {{ 
            background: #f8f9fa; 
            font-weight: bold;
        }}
        .status-badge {{ 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px; 
            font-weight: bold; 
        }}
        .status-completed {{ background: #d4edda; color: #155724; }}
        .status-running {{ background: #d1ecf1; color: #0c5460; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        .eval-score {{ font-weight: bold; padding: 2px 6px; border-radius: 3px; }}
        .eval-high {{ background: #d4edda; color: #155724; }}
        .eval-medium {{ background: #fff3cd; color: #856404; }}
        .eval-low {{ background: #f8d7da; color: #721c24; }}
        .auto-refresh {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #007bff; 
            color: white; 
            padding: 10px 15px; 
            border-radius: 5px; 
            font-size: 14px;
        }}
        .costs {{ 
            background: #fff3cd; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }}
    </style>
    <script>
        // Auto-refresh every 3 seconds
        setInterval(function() {{
            location.reload();
        }}, 3000);
        
        // Update last refresh time
        window.onload = function() {{
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }};
        
        // Show/hide full response
        function showFullResponse(responseId) {{
            var element = document.getElementById(responseId);
            if (element.style.display === 'none') {{
                element.style.display = 'block';
            }} else {{
                element.style.display = 'none';
            }}
        }}
    </script>
</head>
<body>
    <div class="auto-refresh">
        🔄 Auto-refresh: <span id="last-update">Loading...</span>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🧪 LMCA Value Preservation Study</h1>
            <div class="status" id="status">{self.progress_data["status"].upper()}</div>
            <div>Started: {start_time_str}</div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress:.1f}%" id="progress-fill">
                {progress:.1f}%
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="completed-tests">{self.progress_data["completed_tests"]}</div>
                <div class="stat-label">Tests Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-tests">{self.progress_data["total_tests"]}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-cost">${self.progress_data['costs']['total']:.6f}</div>
                <div class="stat-label">Total Cost</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="elapsed-time">{elapsed_str}</div>
                <div class="stat-label">Elapsed Time</div>
            </div>
        </div>
        
        <div class="current-test">
            <h3>🔄 Current Test</h3>
            <div id="current-test-name">{self.progress_data["current_test"]}</div>
        </div>
        
        <h3>📊 Test Results</h3>
        <table class="tests-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Value</th>
                    <th>Test Type</th>
                    <th>System Prompt</th>
                    <th>Question Asked</th>
                    <th>Response</th>
                    <th>Score</th>
                    <th>Cost</th>
                </tr>
            </thead>
            <tbody id="tests-table-body">
                {tests_html}
            </tbody>
        </table>
    </div>
</body>
</html>
        """
        
        # Write updated HTML
        with open(self.dashboard_path, 'w') as f:
            f.write(html_content)
    
    def get_dashboard_path(self) -> str:
        """Get the full path to the dashboard file."""
        return os.path.abspath(self.dashboard_path)