#!/usr/bin/env python3
"""
LangSmith Setup Script for AI Contract Risk Detector
Configures LangSmith tracing for multi-agent workflow monitoring
"""

import os
import json
from pathlib import Path

def setup_langsmith():
    """Setup LangSmith configuration for the project"""
    
    print("🔍 LangSmith Setup for AI Contract Risk Detector")
    print("=" * 50)
    
    # Check for existing .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Error: .env file not found")
        print("   Please create a .env file first with your Groq API key")
        return False
    
    # Read existing .env content
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Check if LangSmith keys are already configured
    if 'LANGCHAIN_API_KEY=' in env_content:
        print("✅ LangSmith API key already configured")
    else:
        print("📝 Adding LangSmith configuration to .env file")
        
        # Add LangSmith configuration
        langsmith_config = """
# LangSmith Configuration for Multi-Agent Monitoring
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=contract-risk-detector
LANGCHAIN_TRACING_V2=true
"""
        
        with open(env_file, 'a') as f:
            f.write(langsmith_config)
        
        print("✅ LangSmith configuration added to .env file")
    
    # Verify langgraph.json exists
    langgraph_file = Path("langgraph.json")
    if not langgraph_file.exists():
        print("❌ Error: langgraph.json file not found")
        return False
    
    print("✅ langgraph.json configuration found")
    
    # Display setup instructions
    print("\n🚀 LangSmith Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Get your LangSmith API key from: https://smith.langchain.com")
    print("2. Update LANGCHAIN_API_KEY in your .env file")
    print("3. Start the application with tracing enabled")
    print("4. Monitor your multi-agent workflow at: https://smith.langchain.com")
    
    print("\n🔧 Configuration Details:")
    print(f"   Project: contract-risk-detector")
    print(f"   Tracing: Enabled (V2)")
    print(f"   Workflow: 5-agent contract analysis pipeline")
    
    print("\n📊 What you can monitor:")
    print("   • Agent execution flow")
    print("   • Token usage and costs")
    print("   • Error tracking and debugging")
    print("   • Performance metrics")
    print("   • Intermediate step analysis")
    
    return True

def create_langsmith_client_example():
    """Create an example script for LangSmith client usage"""
    
    example_code = '''
"""
Example: Using LangSmith Client for Monitoring
"""

from langsmith import Client
import os

def monitor_contract_analysis():
    """Monitor contract analysis workflow in LangSmith"""
    
    # Initialize LangSmith client
    client = Client(
        api_key=os.getenv("LANGCHAIN_API_KEY"),
        api_url="https://api.smith.langchain.com"
    )
    
    # List recent runs
    runs = client.list_runs(
        project_name="contract-risk-detector",
        execution_order="DESC",
        limit=10
    )
    
    print("Recent Contract Analysis Runs:")
    for run in runs:
        print(f"Run ID: {run.id}")
        print(f"Status: {run.end_time - run.start_time:.2f}s")
        print(f"Inputs: {run.inputs.get('filename', 'Unknown')}")
        print(f"Outputs: {run.outputs.get('success', 'Unknown')}")
        print("-" * 40)
    
    # Get detailed run information
    if runs:
        latest_run = runs[0]
        detailed_run = client.read_run(latest_run.id)
        
        print(f"\\nDetailed Analysis for Run {latest_run.id}:")
        print(f"Start Time: {latest_run.start_time}")
        print(f"End Time: {latest_run.end_time}")
        print(f"Total Duration: {latest_run.end_time - latest_run.start_time:.2f}s")
        
        # Show agent steps
        for child in detailed_run.child_runs:
            print(f"Agent: {child.name}")
            print(f"Duration: {child.end_time - child.start_time:.2f}s")
            print(f"Success: {child.outputs.get('success', 'Unknown')}")

if __name__ == "__main__":
    monitor_contract_analysis()
'''
    
    with open("langsmith_example.py", 'w') as f:
        f.write(example_code)
    
    print("📄 Created langsmith_example.py for monitoring")

def main():
    """Main setup function"""
    if setup_langsmith():
        create_langsmith_client_example()
        print("\n🎉 Ready to monitor your multi-agent workflow!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
