"""
LangSmith Monitoring Dashboard for AI Contract Risk Detector
Provides real-time monitoring and analytics for multi-agent workflow
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from langsmith import Client

class ContractAnalysisMonitor:
    """Monitor contract analysis workflow using LangSmith"""
    
    def __init__(self):
        """Initialize the monitor with LangSmith client"""
        self.client = Client(
            api_key=os.getenv("LANGCHAIN_API_KEY"),
            api_url="https://api.smith.langchain.com"
        )
        self.project_name = os.getenv("LANGCHAIN_PROJECT", "contract-risk-detector")
    
    def get_recent_runs(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent analysis runs"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        runs = self.client.list_runs(
            project_name=self.project_name,
            start_time=start_time,
            execution_order="DESC",
            limit=limit
        )
        
        return [
            {
                "run_id": run.id,
                "start_time": run.start_time,
                "end_time": run.end_time,
                "duration": (run.end_time - run.start_time).total_seconds() if run.end_time else None,
                "status": "completed" if run.end_time else "running",
                "inputs": run.inputs or {},
                "outputs": run.outputs or {},
                "error": run.error
            }
            for run in runs
        ]
    
    def get_agent_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for each agent"""
        runs = self.get_recent_runs(hours=hours)
        
        agent_stats = {
            "document_parser": {"count": 0, "avg_duration": 0, "success_rate": 0},
            "clause_extractor": {"count": 0, "avg_duration": 0, "success_rate": 0},
            "risk_analyzer": {"count": 0, "avg_duration": 0, "success_rate": 0},
            "compliance_checker": {"count": 0, "avg_duration": 0, "success_rate": 0},
            "report_generator": {"count": 0, "avg_duration": 0, "success_rate": 0}
        }
        
        for run in runs:
            if run["duration"] and run["status"] == "completed":
                # Get detailed run information
                detailed_run = self.client.read_run(run["run_id"])
                
                for child in detailed_run.child_runs:
                    agent_name = child.name
                    if agent_name in agent_stats:
                        duration = (child.end_time - child.start_time).total_seconds()
                        agent_stats[agent_name]["count"] += 1
                        agent_stats[agent_name]["avg_duration"] += duration
                        agent_stats[agent_name]["success_rate"] += 1 if child.outputs.get("success") else 0
        
        # Calculate averages
        for agent in agent_stats:
            if agent_stats[agent]["count"] > 0:
                agent_stats[agent]["avg_duration"] /= agent_stats[agent]["count"]
                agent_stats[agent]["success_rate"] /= agent_stats[agent]["count"]
                agent_stats[agent]["success_rate"] *= 100
        
        return agent_stats
    
    def get_error_analysis(self, hours: int = 24) -> List[Dict]:
        """Get error analysis for failed runs"""
        runs = self.get_recent_runs(hours=hours)
        
        errors = []
        for run in runs:
            if run["error"] or (run["outputs"] and not run["outputs"].get("success")):
                errors.append({
                    "run_id": run["run_id"],
                    "timestamp": run["start_time"],
                    "error": run["error"] or run["outputs"].get("error", "Unknown error"),
                    "inputs": run["inputs"]
                })
        
        return errors
    
    def get_token_usage(self, hours: int = 24) -> Dict[str, Any]:
        """Get token usage statistics"""
        runs = self.get_recent_runs(hours=hours)
        
        total_tokens = 0
        total_cost = 0
        agent_tokens = {}
        
        for run in runs:
            if run["status"] == "completed":
                detailed_run = self.client.read_run(run["run_id"])
                
                for child in detailed_run.child_runs:
                    agent_name = child.name
                    
                    # Extract token usage from agent runs
                    if hasattr(child, 'outputs') and child.outputs:
                        tokens_used = child.outputs.get("tokens_used", 0)
                        total_tokens += tokens_used
                        
                        if agent_name not in agent_tokens:
                            agent_tokens[agent_name] = 0
                        agent_tokens[agent_name] += tokens_used
        
        # Estimate cost (Groq pricing: ~$0.05 per 1M tokens)
        total_cost = (total_tokens / 1_000_000) * 0.05
        
        return {
            "total_tokens": total_tokens,
            "estimated_cost_usd": total_cost,
            "agent_tokens": agent_tokens,
            "runs_analyzed": len([r for r in runs if r["status"] == "completed"])
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive monitoring report"""
        recent_runs = self.get_recent_runs(hours=24)
        agent_performance = self.get_agent_performance(hours=24)
        errors = self.get_error_analysis(hours=24)
        token_usage = self.get_token_usage(hours=24)
        
        report = f"""
🤖 AI Contract Risk Detector - LangSmith Monitoring Report
{'='*60}

📊 SUMMARY (Last 24 Hours)
• Total Runs: {len(recent_runs)}
• Completed: {len([r for r in recent_runs if r['status'] == 'completed'])}
• Failed: {len([r for r in recent_runs if r['status'] == 'failed'])}
• Success Rate: {(len([r for r in recent_runs if r['status'] == 'completed']) / len(recent_runs) * 100):.1f}%

🔧 AGENT PERFORMANCE
"""
        
        for agent, stats in agent_performance.items():
            if stats["count"] > 0:
                report += f"""
{agent.replace('_', ' ').title()}:
  • Runs: {stats['count']}
  • Avg Duration: {stats['avg_duration']:.2f}s
  • Success Rate: {stats['success_rate']:.1f}%
"""
        
        report += f"""
💰 TOKEN USAGE & COSTS
• Total Tokens: {token_usage['total_tokens']:,}
• Estimated Cost: ${token_usage['estimated_cost_usd']:.4f}
• Cost per Analysis: ${token_usage['estimated_cost_usd'] / max(token_usage['runs_analyzed'], 1):.4f}

🚨 ERRORS (Last 24 Hours)
"""
        
        if errors:
            for error in errors[:5]:  # Show last 5 errors
                report += f"""
• {error['timestamp'].strftime('%H:%M:%S')} - {error['error'][:100]}...
"""
        else:
            report += "• No errors in the last 24 hours! 🎉"
        
        report += f"""
📈 RECOMMENDATIONS
"""
        
        # Add recommendations based on metrics
        if len(errors) > len(recent_runs) * 0.1:
            report += "• High error rate detected - review agent prompts and error handling\n"
        
        avg_duration = sum([r['duration'] for r in recent_runs if r['duration']]) / len([r for r in recent_runs if r['duration']])
        if avg_duration > 300:  # 5 minutes
            report += "• Analysis taking longer than expected - consider optimizing prompts or using faster model\n"
        
        if token_usage['estimated_cost_usd'] > 1.0:
            report += "• High costs detected - consider implementing caching or optimizing token usage\n"
        
        return report

def main():
    """Main monitoring function"""
    monitor = ContractAnalysisMonitor()
    
    print("🔍 AI Contract Risk Detector - LangSmith Monitor")
    print("=" * 50)
    
    # Generate and display report
    report = monitor.generate_report()
    print(report)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"monitoring_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {filename}")

if __name__ == "__main__":
    main()
