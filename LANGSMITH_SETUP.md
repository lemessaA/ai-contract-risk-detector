# LangSmith Setup Guide for AI Contract Risk Detector

## 🔍 Overview

LangSmith provides comprehensive monitoring and debugging capabilities for your multi-agent contract analysis workflow. This guide will help you set up LangSmith to monitor agent performance, track costs, and debug issues.

## 🚀 Quick Setup

### 1. Get LangSmith API Key

1. Go to [LangSmith Console](https://smith.langchain.com)
2. Sign up or log in
3. Navigate to Settings → API Keys
4. Create a new API key
5. Copy the key for configuration

### 2. Configure Environment Variables

Add these to your `.env` file:

```bash
# LangSmith Configuration
LANGCHAIN_API_KEY=ls_your_api_key_here
LANGCHAIN_PROJECT=contract-risk-detector
LANGCHAIN_TRACING_V2=true
```

### 3. Install Dependencies

```bash
cd backend
pip install langsmith>=0.0.60
```

### 4. Run Setup Script

```bash
python setup_langsmith.py
```

## 📊 What You Can Monitor

### Multi-Agent Workflow
- **Document Parser**: Text extraction and cleaning
- **Clause Extractor**: Clause identification and categorization
- **Risk Analyzer**: Risk assessment and scoring
- **Compliance Checker**: Regulatory compliance verification
- **Report Generator**: Final report creation

### Performance Metrics
- Execution time per agent
- Success/failure rates
- Token usage and costs
- Error tracking and debugging
- Intermediate step analysis

### Cost Tracking
- Token usage per agent
- Total analysis costs
- Cost per contract analysis
- Budget monitoring

## 🔧 Using LangSmith Studio

### Access Your Dashboard

1. Go to [LangSmith Studio](https://smith.langchain.com)
2. Select your project: `contract-risk-detector`
3. View real-time monitoring data

### Key Features

#### 📈 Runs Dashboard
- View all contract analysis runs
- Filter by date, status, or performance
- Compare execution times

#### 🔍 Detailed Run Analysis
- Step-by-step agent execution
- Input/output inspection
- Error debugging tools
- Performance bottlenecks

#### 📊 Analytics & Reports
- Agent performance metrics
- Token usage trends
- Cost analysis
- Error patterns

## 📱 Monitoring Scripts

### Basic Monitoring

```python
from langsmith_monitor import ContractAnalysisMonitor

# Initialize monitor
monitor = ContractAnalysisMonitor()

# Get recent runs
runs = monitor.get_recent_runs(hours=24)
print(f"Recent runs: {len(runs)}")

# Generate comprehensive report
report = monitor.generate_report()
print(report)
```

### Advanced Analytics

```python
# Agent performance
agent_stats = monitor.get_agent_performance(hours=24)
for agent, stats in agent_stats.items():
    print(f"{agent}: {stats['success_rate']:.1f}% success rate")

# Error analysis
errors = monitor.get_error_analysis(hours=24)
for error in errors:
    print(f"Error: {error['error']}")

# Token usage
token_usage = monitor.get_token_usage(hours=24)
print(f"Total cost: ${token_usage['estimated_cost_usd']:.4f}")
```

## 🛠️ Integration with Your Application

### Automatic Tracing

The orchestrator automatically enables LangSmith tracing when API key is configured:

```python
# In contract_agent.py
if os.getenv("LANGCHAIN_API_KEY"):
    self.tracer = LangChainTracer(
        project_name=os.getenv("LANGCHAIN_PROJECT", "contract-risk-detector")
    )
```

### Custom Tracing

Add custom traces for specific operations:

```python
from langsmith import Client

client = Client()

# Create custom run
with client.trace(
    name="custom_contract_analysis",
    inputs={"contract_file": "contract.pdf"},
    project_name="contract-risk-detector"
):
    # Your custom analysis logic
    result = analyze_contract_custom()
    return {"result": result}
```

## 📋 Best Practices

### 1. Project Organization
- Use consistent project names
- Tag runs with metadata
- Group related analyses

### 2. Cost Management
- Monitor token usage regularly
- Set up cost alerts
- Optimize prompts for efficiency

### 3. Error Handling
- Log all errors with context
- Use structured error messages
- Implement retry logic

### 4. Performance Optimization
- Track execution times
- Identify bottlenecks
- Optimize agent prompts

## 🔍 Debugging with LangSmith

### Common Issues

#### Slow Performance
1. Check agent execution times in Studio
2. Look for token-heavy operations
3. Optimize prompts for conciseness

#### High Error Rates
1. Review error patterns in Studio
2. Check input validation
3. Improve error handling

#### Cost Overruns
1. Monitor token usage trends
2. Identify inefficient agents
3. Implement caching strategies

### Debugging Workflow

1. **Identify the Problem**: Use Studio to locate failing runs
2. **Examine Inputs**: Check if inputs are valid
3. **Review Agent Steps**: Look at intermediate outputs
4. **Analyze Errors**: Review error messages and stack traces
5. **Test Fixes**: Implement and test solutions

## 📈 Advanced Features

### Comparative Analysis
Compare different contract analysis approaches:

```python
# Compare different prompt strategies
with client.trace(name="experiment_v1", inputs={"prompt_version": "v1"}):
    result_v1 = analyze_with_prompt_v1()

with client.trace(name="experiment_v2", inputs={"prompt_version": "v2"}):
    result_v2 = analyze_with_prompt_v2()

# Compare results in Studio
```

### A/B Testing
Test different configurations:

```python
import random

# Random assignment
use_new_method = random.choice([True, False])

with client.trace(
    name="ab_test",
    inputs={"method": "new" if use_new_method else "old"},
    tags=["experiment"]
):
    if use_new_method:
        result = analyze_with_new_method()
    else:
        result = analyze_with_old_method()
```

### Performance Benchmarking
Track performance over time:

```python
import time

start_time = time.time()
result = analyze_contract()
duration = time.time() - start_time

with client.trace(
    name="benchmark",
    inputs={"file_size": file_size},
    outputs={"duration": duration, "success": result["success"]}
):
    pass  # Trace recorded automatically
```

## 🚨 Troubleshooting

### Common Setup Issues

#### API Key Not Working
```bash
# Verify API key format
echo $LANGCHAIN_API_KEY

# Test connection
python -c "from langsmith import Client; Client()"
```

#### Project Not Showing Up
- Check project name spelling
- Verify API key permissions
- Ensure tracing is enabled

#### No Data in Studio
- Confirm LANGCHAIN_TRACING_V2=true
- Check if application is running
- Verify network connectivity

### Performance Issues

#### High Latency
- Check network connectivity to LangSmith
- Reduce trace detail level
- Use local tracing for development

#### Memory Issues
- Limit trace history
- Clean up old runs
- Use sampling for high-volume applications

## 📞 Support

- **LangSmith Documentation**: https://docs.smith.langchain.com
- **GitHub Issues**: https://github.com/langchain-ai/langsmith
- **Community**: https://discord.gg/langchain

## 🔄 Continuous Monitoring

Set up automated monitoring:

```python
# Add to your application startup
import schedule
from langsmith_monitor import ContractAnalysisMonitor

def daily_report():
    monitor = ContractAnalysisMonitor()
    report = monitor.generate_report()
    
    # Send to Slack/email/monitoring system
    send_alert(report)

# Schedule daily reports
schedule.every().day.at("09:00").do(daily_report)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

## 📊 Metrics Dashboard

Create a custom metrics dashboard:

```python
import streamlit as st
from langsmith_monitor import ContractAnalysisMonitor

st.title("Contract Analysis Monitor")
monitor = ContractAnalysisMonitor()

# Real-time metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Runs", len(monitor.get_recent_runs(hours=24)))

with col2:
    st.metric("Success Rate", f"{monitor.get_success_rate():.1f}%")

with col3:
    st.metric("Est. Cost", f"${monitor.get_cost_estimate():.4f}")

# Performance charts
agent_stats = monitor.get_agent_performance(hours=24)
st.bar_chart(agent_stats)
```

This comprehensive setup will give you full visibility into your multi-agent contract analysis workflow! 🎯
