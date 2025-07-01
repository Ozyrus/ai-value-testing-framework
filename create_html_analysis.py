#!/usr/bin/env python3
"""Create HTML manual analysis table for experimental results."""

import sqlite3
from collections import defaultdict

def create_html_analysis():
    """Create HTML analysis table from experimental results."""
    
    conn = sqlite3.connect('data/results.db')
    cursor = conn.cursor()
    
    # Get all results
    query = """
    SELECT 
        model_name,
        test_category,
        value_direction, 
        value_name,
        automated_score,
        session_id
    FROM test_results 
    ORDER BY value_name, test_category, value_direction, session_id
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # Process results
    results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for row in rows:
        model_name, test_category, value_direction, value_name, automated_score, session_id = row
        
        # Extract temperature from model_name (e.g., "openai-chatgpt-4o-mini_T0.7" -> "0.7")
        temp = model_name.split('_T')[1] if '_T' in model_name else 'unknown'
        
        scenario = f"{test_category}_{value_direction}"
        results[temp][value_name][scenario].append(automated_score)
    
    # Generate HTML
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self-Modifying Agentic Systems - Manual Analysis</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
        }
        .value-section {
            margin-bottom: 40px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        th, td {
            padding: 12px 8px;
            text-align: center;
            border: 1px solid #ddd;
        }
        th {
            background: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        tr:hover {
            background: #e3f2fd;
        }
        .temp-header {
            background: #2c3e50 !important;
            color: white;
        }
        .scenario-header {
            background: #34495e !important;
            color: white;
            min-width: 120px;
            padding: 8px 4px;
        }
        .success-rate {
            font-weight: bold;
        }
        .perfect { color: #27ae60; }
        .partial { color: #f39c12; }
        .failed { color: #e74c3c; }
        .summary {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
        }
        .key-finding {
            background: #d5efef;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            font-size: 12px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Self-Modifying Agentic Systems<br>Identity Preservation Study - Manual Analysis</h1>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #27ae60;"></div>
                <span>100% Success</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f39c12;"></div>
                <span>Partial Success</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e74c3c;"></div>
                <span>0% Success</span>
            </div>
        </div>
"""
    
    # Get all values from database dynamically
    values = list(set(row[3] for row in rows))  # row[3] is value_name
    values.sort()  # Sort for consistent ordering
    value_titles = [value.replace('_', ' ').title() for value in values]
    
    for value, title in zip(values, value_titles):
        html_content += f"""
        <div class="value-section">
            <h2>📊 {title}</h2>
            <table>
                <thead>
                    <tr>
                        <th class="temp-header">Temperature</th>
                        <th class="scenario-header">Natural Positive</th>
                        <th class="scenario-header">Natural Negative</th>
                        <th class="scenario-header">Instructed Positive</th>
                        <th class="scenario-header">Instructed Negative</th>
                        <th class="scenario-header">Resistance Positive</th>
                        <th class="scenario-header">Resistance Negative</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add data rows for each temperature
        for temp in sorted(results.keys()):
            if temp == 'unknown':
                continue
                
            html_content += f"                    <tr>\n                        <td class=\"temp-header\">{temp}</td>\n"
            
            scenarios = ['natural_positive', 'natural_negative', 'instructed_positive', 
                        'instructed_negative', 'resistance_positive', 'resistance_negative']
            
            for scenario in scenarios:
                if value in results[temp] and scenario in results[temp][value]:
                    scores = results[temp][value][scenario]
                    total_runs = len(scores)
                    successes = sum(scores)
                    success_rate = (successes / total_runs) * 100 if total_runs > 0 else 0
                    
                    # Determine color class
                    if success_rate == 100:
                        color_class = "perfect"
                    elif success_rate == 0:
                        color_class = "failed"
                    else:
                        color_class = "partial"
                    
                    cell_content = f'<span class="success-rate {color_class}">{success_rate:.0f}%</span><br><small>({successes}/{total_runs})</small>'
                else:
                    cell_content = '<span class="failed">No data</span>'
                
                html_content += f"                        <td>{cell_content}</td>\n"
            
            html_content += "                    </tr>\n"
        
        html_content += """                </tbody>
            </table>
        </div>
"""
    
    # Add summary section
    html_content += f"""
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <div class="key-finding">
                <strong>Tested Values:</strong> {len(values)} values across {len(set(row[4] for row in rows))} test scenarios each
            </div>
            <div class="key-finding">
                <strong>Data Coverage:</strong> {len(rows)} total tests across {len(set(row[5] for row in rows))} experimental sessions
            </div>
            <div class="key-finding">
                <strong>Analysis:</strong> Review the data patterns above to identify malleable vs immutable AI values, instruction following vs resistance patterns, and temperature effects.
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px; color: #7f8c8d; font-size: 12px;">
            Generated from experimental data • Total tests analyzed: {len(rows)} across {len(set(row[5] for row in rows))} sessions
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open('manual_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ HTML analysis table created: manual_analysis.html")
    
    # Count tests by temperature
    temp_counts = {}
    for row in rows:
        temp = row[0].split('_T')[1] if '_T' in row[0] else 'unknown'
        temp_counts[temp] = temp_counts.get(temp, 0) + 1
    
    temp_summary = ", ".join([f"Temperature {temp} = {count} tests" for temp, count in sorted(temp_counts.items())])
    print(f"📊 Dataset: {temp_summary}")

if __name__ == "__main__":
    create_html_analysis()