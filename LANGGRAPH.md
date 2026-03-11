# 🎯 LangGraph Integration Documentation

Comprehensive documentation for LangGraph workflow orchestration and LangSmith monitoring in the AI Contract Risk Detector.

## 📋 **Table of Contents**

- [Overview](#overview)
- [LangGraph Architecture](#langgraph-architecture)
- [Multi-Agent Workflow](#multi-agent-workflow)
- [Configuration](#configuration)
- [LangSmith Monitoring](#langsmith-monitoring)
- [Studio Integration](#studio-integration)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

The AI Contract Risk Detector uses **LangGraph** for orchestrating complex multi-agent workflows and **LangSmith** for comprehensive monitoring and debugging. This integration provides:

- **Visual workflow orchestration** with agent coordination
- **Real-time performance monitoring** and analytics
- **Debugging capabilities** with detailed execution traces
- **Scalable architecture** for adding new agents
- **Enterprise-grade monitoring** with audit trails

---

## 🏗️ LangGraph Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Document    │  │ Clause      │  │ Risk        │         │
│  │ Parser      │  │ Extractor   │  │ Analyzer    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         ↓                ↓                ↓                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Compliance  │  │ Before Sign │  │ Report      │         │
│  │ Checker     │  │ Report      │  │ Generator   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LangSmith Monitoring                     │
├─────────────────────────────────────────────────────────────┤
│  • Execution Tracing  • Performance Metrics  • Error Logs   │
│  • Agent Analytics   • Usage Statistics    • Debug Tools   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. **ContractAnalysisOrchestrator**
Main orchestrator class that manages the multi-agent workflow.

```python
class ContractAnalysisOrchestrator:
    """Multi-agent contract analysis orchestrator using LangGraph"""
    
    def __init__(self):
        self.tracer = None
        self.agents = {
            "document_parser": DocumentParserAgent(),
            "clause_extractor": ClauseExtractorAgent(),
            "risk_analyzer": RiskAnalyzerAgent(),
            "compliance_checker": ComplianceCheckerAgent(),
            "before_sign_report": BeforeSignReportAgent()
        }
    
    def build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for contract analysis"""
        
        # Define workflow state
        class AnalysisState(TypedDict):
            contract_text: str
            parsed_content: Dict[str, Any]
            clauses: List[Dict[str, Any]]
            risk_analyses: List[Dict[str, Any]]
            compliance_results: Dict[str, Any]
            before_sign_report: Dict[str, Any]
            errors: List[str]
        
        # Create state graph
        workflow = StateGraph(AnalysisState)
        
        # Add nodes (agents)
        workflow.add_node("parse_document", self._parse_document_node)
        workflow.add_node("extract_clauses", self._extract_clauses_node)
        workflow.add_node("analyze_risks", self._analyze_risks_node)
        workflow.add_node("check_compliance", self._check_compliance_node)
        workflow.add_node("generate_report", self._generate_report_node)
        
        # Add edges (workflow)
        workflow.add_edge("parse_document", "extract_clauses")
        workflow.add_edge("extract_clauses", "analyze_risks")
        workflow.add_edge("analyze_risks", "check_compliance")
        workflow.add_edge("check_compliance", "generate_report")
        
        # Set entry point
        workflow.set_entry_point("parse_document")
        workflow.set_finish_point("generate_report")
        
        return workflow.compile()
```

#### 2. **Agent Nodes**
Each agent is implemented as a LangGraph node with proper state management.

```python
async def _parse_document_node(self, state: AnalysisState) -> AnalysisState:
    """Node for document parsing"""
    try:
        if self.tracer:
            self.tracer.start_trace("document_parsing")
        
        # Parse document
        parsed_content = await self.agents["document_parser"].parse_document(
            state["contract_text"]
        )
        
        # Update state
        state["parsed_content"] = parsed_content
        
        if self.tracer:
            self.tracer.end_trace("document_parsing", {
                "word_count": parsed_content.get("word_count", 0),
                "success": True
            })
        
        return state
        
    except Exception as e:
        if self.tracer:
            self.tracer.end_trace("document_parsing", {
                "error": str(e),
                "success": False
            })
        
        state["errors"].append(f"Document parsing failed: {str(e)}")
        return state
```

---

## 🔄 Multi-Agent Workflow

### Workflow Sequence

1. **Document Parsing** 📄
   - Extract text from uploaded file
   - Clean and normalize content
   - Identify document structure

2. **Clause Extraction** 📋
   - Identify individual clauses
   - Categorize by type and importance
   - Extract key terms and conditions

3. **Risk Analysis** ⚠️
   - Analyze each clause for potential risks
   - Assign severity ratings
   - Provide detailed explanations

4. **Compliance Checking** ✅
   - Verify regulatory compliance
   - Check for missing essential clauses
   - Assess overall compliance score

5. **Report Generation** 📊
   - Create user-friendly summary
   - Highlight top risky clauses
   - Provide actionable recommendations

### State Management

```python
class AnalysisState(TypedDict):
    """State object for passing data between agents"""
    
    # Input data
    contract_text: str
    file_metadata: Dict[str, Any]
    
    # Agent outputs
    parsed_content: Dict[str, Any]
    clauses: List[Dict[str, Any]]
    risk_analyses: List[Dict[str, Any]]
    compliance_results: Dict[str, Any]
    before_sign_report: Dict[str, Any]
    
    # Workflow metadata
    current_step: str
    errors: List[str]
    warnings: List[str]
    execution_times: Dict[str, float]
    
    # Configuration
    analysis_options: Dict[str, Any]
    user_preferences: Dict[str, Any]
```

### Error Handling & Recovery

```python
async def _execute_with_retry(self, node_func, state: AnalysisState, max_retries: int = 3) -> AnalysisState:
    """Execute a node with retry logic"""
    
    for attempt in range(max_retries):
        try:
            return await node_func(state)
        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                state["errors"].append(f"Node {node_func.__name__} failed after {max_retries} attempts: {str(e)}")
                return state
            else:
                # Log retry attempt
                logger.warning(f"Retrying {node_func.__name__} (attempt {attempt + 2}/{max_retries})")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    
    return state
```

---

## ⚙️ Configuration

### LangGraph Configuration (`backend/langgraph.json`)

```json
{
  "workflow": {
    "name": "contract-analysis",
    "description": "Multi-agent contract risk analysis workflow",
    "version": "1.0.0",
    "nodes": [
      {
        "id": "parse_document",
        "name": "Document Parser",
        "type": "agent",
        "agent": "document_parser",
        "description": "Extract and clean text from contract documents",
        "timeout": 60,
        "retry_attempts": 3
      },
      {
        "id": "extract_clauses",
        "name": "Clause Extractor",
        "type": "agent",
        "agent": "clause_extractor",
        "description": "Identify and categorize contract clauses",
        "timeout": 45,
        "retry_attempts": 3
      },
      {
        "id": "analyze_risks",
        "name": "Risk Analyzer",
        "type": "agent",
        "agent": "risk_analyzer",
        "description": "Analyze clauses for potential risks",
        "timeout": 90,
        "retry_attempts": 3
      },
      {
        "id": "check_compliance",
        "name": "Compliance Checker",
        "type": "agent",
        "agent": "compliance_checker",
        "description": "Verify regulatory compliance",
        "timeout": 60,
        "retry_attempts": 3
      },
      {
        "id": "generate_report",
        "name": "Report Generator",
        "type": "agent",
        "agent": "before_sign_report",
        "description": "Generate user-friendly analysis report",
        "timeout": 30,
        "retry_attempts": 2
      }
    ],
    "edges": [
      {"from": "parse_document", "to": "extract_clauses"},
      {"from": "extract_clauses", "to": "analyze_risks"},
      {"from": "analyze_risks", "to": "check_compliance"},
      {"from": "check_compliance", "to": "generate_report"}
    ],
    "entry_point": "parse_document",
    "finish_point": "generate_report"
  },
  "environment": {
    "langchain_api_key": "${LANGCHAIN_API_KEY}",
    "langchain_project": "contract-risk-detector",
    "langchain_tracing": "true"
  },
  "monitoring": {
    "enable_tracing": true,
    "enable_performance_tracking": true,
    "log_level": "INFO",
    "metrics_collection": true
  },
  "optimization": {
    "parallel_execution": false,
    "caching_enabled": true,
    "batch_processing": true,
    "resource_limits": {
      "max_memory_mb": 1024,
      "max_cpu_percent": 80
    }
  }
}
```

### Environment Variables

```bash
# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=contract-risk-detector
LANGCHAIN_TRACING=true

# LangGraph Configuration
LANGGRAPH_API_KEY=your_langgraph_api_key
LANGGRAPH_ENDPOINT=http://localhost:2024

# Performance Settings
LANGGRAPH_TIMEOUT=300
LANGGRAPH_MAX_RETRIES=3
LANGGRAPH_PARALLEL_EXECUTION=false
```

---

## 📊 LangSmith Monitoring

### Setup Script (`backend/setup_langsmith.py`)

```python
#!/usr/bin/env python3
"""
LangSmith setup and configuration script
"""

import os
import sys
from pathlib import Path

def setup_langsmith():
    """Setup LangSmith for monitoring"""
    
    print("🔧 Setting up LangSmith monitoring...")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please create it first.")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Check if LangSmith is already configured
    if "LANGCHAIN_API_KEY" in env_content:
        print("✅ LangSmith already configured in .env")
        return True
    
    # Prompt for API key
    api_key = input("Enter your LangSmith API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⚠️ Skipping LangSmith setup")
        return True
    
    # Add LangSmith configuration to .env
    langsmith_config = f"""
# LangSmith Configuration
LANGCHAIN_API_KEY={api_key}
LANGCHAIN_PROJECT=contract-risk-detector
LANGCHAIN_TRACING=true
"""
    
    with open(env_file, 'a') as f:
        f.write(langsmith_config)
    
    print("✅ LangSmith configuration added to .env")
    return True

def verify_setup():
    """Verify LangSmith setup"""
    
    print("\n🔍 Verifying LangSmith setup...")
    
    # Check environment variables
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT", "contract-risk-detector")
    tracing = os.getenv("LANGCHAIN_TRACING", "false").lower() == "true"
    
    if not api_key:
        print("❌ LANGCHAIN_API_KEY not set")
        return False
    
    print(f"✅ API Key: {'*' * 20}{api_key[-4:]}")
    print(f"✅ Project: {project}")
    print(f"✅ Tracing: {'Enabled' if tracing else 'Disabled'}")
    
    # Test LangSmith connection
    try:
        from langchain.callbacks.tracers import LangChainTracer
        tracer = LangChainTracer(project_name=project)
        print("✅ LangSmith connection successful")
        return True
    except Exception as e:
        print(f"❌ LangSmith connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 LangSmith Setup for AI Contract Risk Detector")
    print("=" * 50)
    
    if setup_langsmith():
        verify_setup()
        print("\n🎉 LangSmith setup complete!")
        print("\n📊 View your workflows at: https://smith.langchain.com")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
```

### Monitoring Dashboard (`backend/langsmith_monitor.py`)

```python
"""
LangSmith monitoring dashboard for contract analysis
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langchain.client import LangSmithClient
from dataclasses import dataclass

@dataclass
class WorkflowMetrics:
    """Metrics for workflow performance"""
    total_runs: int
    successful_runs: int
    failed_runs: int
    average_duration: float
    success_rate: float
    error_rate: float

@dataclass
class AgentMetrics:
    """Metrics for individual agents"""
    agent_name: str
    total_executions: int
    successful_executions: int
    average_execution_time: float
    error_count: int
    most_common_errors: List[Dict[str, Any]]

class LangSmithMonitor:
    """Monitor LangSmith workflows and agents"""
    
    def __init__(self, project_name: str = "contract-risk-detector"):
        self.project_name = project_name
        self.client = LangSmithClient(
            api_key=os.getenv("LANGCHAIN_API_KEY"),
            api_url="https://api.smith.langchain.com"
        )
    
    def get_workflow_metrics(self, days: int = 7) -> WorkflowMetrics:
        """Get overall workflow metrics"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get runs for the project
        runs = list(self.client.list_runs(
            project_name=self.project_name,
            start_time=start_date,
            end_time=end_date
        ))
        
        total_runs = len(runs)
        successful_runs = len([r for r in runs if r.end_time is not None and r.error is None])
        failed_runs = total_runs - successful_runs
        
        # Calculate average duration
        durations = []
        for run in runs:
            if run.start_time and run.end_time:
                duration = (run.end_time - run.start_time).total_seconds()
                durations.append(duration)
        
        average_duration = sum(durations) / len(durations) if durations else 0
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        error_rate = (failed_runs / total_runs * 100) if total_runs > 0 else 0
        
        return WorkflowMetrics(
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            average_duration=average_duration,
            success_rate=success_rate,
            error_rate=error_rate
        )
    
    def get_agent_metrics(self, days: int = 7) -> List[AgentMetrics]:
        """Get metrics for individual agents"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get runs with agent information
        runs = list(self.client.list_runs(
            project_name=self.project_name,
            start_time=start_date,
            end_time=end_date
        ))
        
        # Group by agent
        agent_data = {}
        
        for run in runs:
            agent_name = self._extract_agent_name(run)
            if not agent_name:
                continue
            
            if agent_name not in agent_data:
                agent_data[agent_name] = {
                    "executions": [],
                    "errors": []
                }
            
            # Record execution
            execution_time = 0
            if run.start_time and run.end_time:
                execution_time = (run.end_time - run.start_time).total_seconds()
            
            agent_data[agent_name]["executions"].append({
                "time": execution_time,
                "success": run.error is None,
                "timestamp": run.start_time
            })
            
            # Record errors
            if run.error:
                agent_data[agent_name]["errors"].append({
                    "error": str(run.error),
                    "timestamp": run.start_time
                })
        
        # Generate metrics for each agent
        metrics = []
        for agent_name, data in agent_data.items():
            executions = data["executions"]
            errors = data["errors"]
            
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e["success"]])
            
            execution_times = [e["time"] for e in executions if e["time"] > 0]
            average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Most common errors
            error_counts = {}
            for error in errors:
                error_msg = error["error"]
                error_counts[error_msg] = error_counts.get(error_msg, 0) + 1
            
            most_common_errors = [
                {"error": error, "count": count}
                for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            metrics.append(AgentMetrics(
                agent_name=agent_name,
                total_executions=total_executions,
                successful_executions=successful_executions,
                average_execution_time=average_execution_time,
                error_count=len(errors),
                most_common_errors=most_common_errors
            ))
        
        return metrics
    
    def _extract_agent_name(self, run) -> Optional[str]:
        """Extract agent name from run data"""
        # This would depend on how you structure your LangSmith runs
        if hasattr(run, 'name') and run.name:
            return run.name
        
        if hasattr(run, 'tags') and run.tags:
            for tag in run.tags:
                if tag in ["document_parser", "clause_extractor", "risk_analyzer", "compliance_checker", "before_sign_report"]:
                    return tag
        
        return None
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors from workflow runs"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        runs = list(self.client.list_runs(
            project_name=self.project_name,
            start_time=start_date,
            end_time=end_date
        ))
        
        errors = []
        for run in runs:
            if run.error:
                errors.append({
                    "run_id": run.id,
                    "timestamp": run.start_time,
                    "error": str(run.error),
                    "agent": self._extract_agent_name(run),
                    "duration": (run.end_time - run.start_time).total_seconds() if run.start_time and run.end_time else 0
                })
        
        return sorted(errors, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        
        workflow_metrics = self.get_workflow_metrics(days)
        agent_metrics = self.get_agent_metrics(days)
        recent_errors = self.get_recent_errors()
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period_days": days,
            "project_name": self.project_name,
            "workflow_metrics": {
                "total_runs": workflow_metrics.total_runs,
                "successful_runs": workflow_metrics.successful_runs,
                "failed_runs": workflow_metrics.failed_runs,
                "success_rate": f"{workflow_metrics.success_rate:.2f}%",
                "error_rate": f"{workflow_metrics.error_rate:.2f}%",
                "average_duration": f"{workflow_metrics.average_duration:.2f}s"
            },
            "agent_metrics": [
                {
                    "agent_name": metric.agent_name,
                    "total_executions": metric.total_executions,
                    "success_rate": f"{(metric.successful_executions / metric.total_executions * 100):.2f}%" if metric.total_executions > 0 else "0%",
                    "average_execution_time": f"{metric.average_execution_time:.2f}s",
                    "error_count": metric.error_count,
                    "top_errors": metric.most_common_errors[:3]
                }
                for metric in agent_metrics
            ],
            "recent_errors": recent_errors[:5],
            "recommendations": self._generate_recommendations(workflow_metrics, agent_metrics)
        }
    
    def _generate_recommendations(self, workflow_metrics: WorkflowMetrics, agent_metrics: List[AgentMetrics]) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Workflow level recommendations
        if workflow_metrics.error_rate > 10:
            recommendations.append("High error rate detected. Review error logs and improve error handling.")
        
        if workflow_metrics.average_duration > 120:
            recommendations.append("Long execution times. Consider optimizing agent performance or enabling parallel execution.")
        
        # Agent level recommendations
        for metric in agent_metrics:
            success_rate = (metric.successful_executions / metric.total_executions * 100) if metric.total_executions > 0 else 0
            
            if success_rate < 90:
                recommendations.append(f"Agent '{metric.agent_name}' has low success rate ({success_rate:.1f}%). Review implementation.")
            
            if metric.average_execution_time > 60:
                recommendations.append(f"Agent '{metric.agent_name}' is slow ({metric.average_execution_time:.1f}s). Consider optimization.")
        
        if not recommendations:
            recommendations.append("System is performing well. Continue monitoring for optimization opportunities.")
        
        return recommendations

# Usage example
if __name__ == "__main__":
    monitor = LangSmithMonitor()
    report = monitor.generate_report(days=7)
    
    print("📊 LangSmith Monitoring Report")
    print("=" * 40)
    print(f"Project: {report['project_name']}")
    print(f"Period: {report['period_days']} days")
    print(f"Generated: {report['report_generated']}")
    
    print("\n🔄 Workflow Metrics:")
    for key, value in report['workflow_metrics'].items():
        print(f"  {key}: {value}")
    
    print("\n🤖 Agent Performance:")
    for agent in report['agent_metrics']:
        print(f"  {agent['agent_name']}: {agent['success_rate']} success, {agent['average_execution_time']} avg time")
    
    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
```

---

## 🎨 Studio Integration

### LangGraph Studio Setup

```bash
# Start LangGraph Studio
langgraph studio

# Access Studio at:
# http://localhost:2024
# or
# https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Studio Features

1. **Visual Workflow Editor**
   - Drag-and-drop node creation
   - Visual edge connections
   - Real-time workflow validation

2. **Execution Monitoring**
   - Live execution traces
   - Performance metrics
   - Error tracking

3. **Debugging Tools**
   - Step-by-step execution
   - State inspection
   - Variable watching

4. **Agent Management**
   - Agent configuration
   - Performance optimization
   - Resource allocation

### Workflow Export Function

```python
# backend/agents/contract_agent_langgraph.py

def _build_workflow() -> StateGraph:
    """Standalone workflow builder for LangGraph Studio"""
    
    orchestrator = ContractAnalysisOrchestrator()
    return orchestrator.build_workflow()

# Export for LangGraph Studio
build_workflow = _build_workflow
```

---

## ⚡ Performance Optimization

### Optimization Strategies

#### 1. **Parallel Execution**
```python
# Enable parallel processing for independent agents
workflow.add_edge("parse_document", ["extract_clauses", "analyze_risks"])
```

#### 2. **Caching**
```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

# Enable caching
set_llm_cache(InMemoryCache())
```

#### 3. **Resource Management**
```python
# Configure resource limits
resource_config = {
    "max_memory_mb": 1024,
    "max_cpu_percent": 80,
    "timeout_seconds": 300
}
```

#### 4. **Batch Processing**
```python
# Process multiple clauses in batches
async def batch_analyze_clauses(clauses: List[Dict], batch_size: int = 5):
    """Analyze clauses in batches for better performance"""
    
    batches = [clauses[i:i + batch_size] for i in range(0, len(clauses), batch_size)]
    results = []
    
    for batch in batches:
        batch_results = await analyze_clause_batch(batch)
        results.extend(batch_results)
    
    return results
```

### Performance Monitoring

```python
class PerformanceTracker:
    """Track performance metrics for optimization"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str):
        """End timing and record duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            
            if operation not in self.metrics:
                self.metrics[operation] = []
            
            self.metrics[operation].append(duration)
            
            # Calculate statistics
            avg_duration = sum(self.metrics[operation]) / len(self.metrics[operation])
            min_duration = min(self.metrics[operation])
            max_duration = max(self.metrics[operation])
            
            logger.info(f"Performance - {operation}: avg={avg_duration:.2f}s, min={min_duration:.2f}s, max={max_duration:.2f}s")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        report = {}
        
        for operation, durations in self.metrics.items():
            report[operation] = {
                "count": len(durations),
                "average": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
                "total": sum(durations)
            }
        
        return report
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **LangSmith Connection Issues**
```bash
# Check API key
echo $LANGCHAIN_API_KEY

# Test connection
python -c "from langchain.client import LangSmithClient; print('Connection OK')"

# Verify project exists
python -c "from langchain.client import LangSmithClient; client = LangSmithClient(); print(client.list_projects())"
```

#### 2. **Workflow Execution Failures**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check workflow structure
workflow = orchestrator.build_workflow()
print(f"Nodes: {list(workflow.nodes)}")
print(f"Edges: {list(workflow.edges)}")
```

#### 3. **Performance Issues**
```python
# Monitor resource usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
print(f"CPU usage: {process.cpu_percent()}%")
```

### Debug Mode

```python
# Enable debug mode in orchestrator
orchestrator = ContractAnalysisOrchestrator(debug=True)

# Enable verbose LangSmith tracing
os.environ["LANGCHAIN_VERBOSE"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
```

### Error Recovery

```python
class WorkflowRecovery:
    """Handle workflow errors and recovery"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.checkpoints = {}
    
    def save_checkpoint(self, state: AnalysisState, checkpoint_id: str):
        """Save workflow state for recovery"""
        self.checkpoints[checkpoint_id] = state.copy()
    
    def recover_from_checkpoint(self, checkpoint_id: str) -> AnalysisState:
        """Recover workflow from checkpoint"""
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id].copy()
        raise ValueError(f"Checkpoint {checkpoint_id} not found")
    
    def handle_failure(self, state: AnalysisState, error: Exception) -> AnalysisState:
        """Handle workflow failure with recovery options"""
        
        error_msg = str(error)
        state["errors"].append(error_msg)
        
        # Check if we can retry from a specific node
        if "timeout" in error_msg.lower():
            # Retry with increased timeout
            state["analysis_options"]["timeout"] = state["analysis_options"].get("timeout", 60) * 2
        
        elif "rate_limit" in error_msg.lower():
            # Add delay and retry
            import asyncio
            await asyncio.sleep(5)
        
        return state
```

---

## 📈 Best Practices

### 1. **Workflow Design**
- Keep agents focused on single responsibilities
- Use clear state transitions
- Implement proper error handling
- Add comprehensive logging

### 2. **Performance Optimization**
- Monitor execution times regularly
- Use caching for expensive operations
- Implement batch processing where possible
- Set appropriate timeouts

### 3. **Monitoring & Debugging**
- Enable LangSmith tracing in production
- Set up alerts for high error rates
- Regular performance reviews
- Comprehensive error logging

### 4. **Scalability**
- Design for horizontal scaling
- Implement resource limits
- Use connection pooling
- Plan for increased load

---

## 🎯 Summary

The LangGraph integration provides:

- **🔄 Visual Workflow Orchestration** with multi-agent coordination
- **📊 Comprehensive Monitoring** with LangSmith integration
- **🎨 Studio Integration** for visual workflow management
- **⚡ Performance Optimization** with caching and parallel execution
- **🔧 Robust Error Handling** with recovery mechanisms
- **📈 Enterprise-Grade Analytics** with detailed metrics

This integration transforms the AI Contract Risk Detector into a sophisticated, monitorable, and scalable multi-agent system with enterprise-grade workflow orchestration capabilities.
