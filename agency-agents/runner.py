#!/usr/bin/env python3
"""
Agency Agents Runner for OpenClaw
Quickly switch between AI agent personalities
"""

import os
import sys
import json
import argparse

AGENTS_DIR = os.path.expanduser("~/.openclaw/workspace/agency-agents")

def list_agents():
    """List all available agents"""
    agents = []
    
    categories = [
        "engineering", "marketing", "design", "product",
        "project-management", "testing", "specialized", 
        "support", "strategy", "spatial-computing", "game-development"
    ]
    
    for category in categories:
        cat_path = os.path.join(AGENTS_DIR, category)
        if os.path.exists(cat_path):
            files = [f for f in os.listdir(cat_path) if f.endswith('.md')]
            for f in files:
                agent_name = f.replace('.md', '').replace(f'{category}-', '')
                agents.append({
                    "name": agent_name,
                    "category": category,
                    "file": f
                })
    
    return agents

def get_agent_file(agent_name):
    """Find agent file by name"""
    agents = list_agents()
    for agent in agents:
        if agent_name.lower() in agent["name"].lower():
            return os.path.join(AGENTS_DIR, agent["category"], agent["file"])
    return None

def read_agent_persona(agent_file):
    """Read and return agent persona content"""
    try:
        with open(agent_file, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading agent: {e}"

def main():
    parser = argparse.ArgumentParser(description="Agency Agents for OpenClaw")
    parser.add_argument("command", choices=["list", "activate", "search"], help="Command")
    parser.add_argument("--agent", "-a", help="Agent name to activate")
    parser.add_argument("--category", "-c", help="Filter by category")
    
    args = parser.parse_args()
    
    if args.command == "list":
        agents = list_agents()
        
        if args.category:
            agents = [a for a in agents if a["category"] == args.category]
        
        print(f"🎭 Available Agents ({len(agents)} total):\n")
        
        current_cat = None
        for agent in sorted(agents, key=lambda x: x["category"]):
            if agent["category"] != current_cat:
                current_cat = agent["category"]
                print(f"\n📁 {current_cat.upper()}")
            print(f"  • {agent['name']}")
    
    elif args.command == "activate":
        if not args.agent:
            print("❌ Please specify --agent <name>")
            sys.exit(1)
        
        agent_file = get_agent_file(args.agent)
        if not agent_file:
            print(f"❌ Agent '{args.agent}' not found")
            print("💡 Use 'list' command to see available agents")
            sys.exit(1)
        
        persona = read_agent_persona(agent_file)
        
        print(f"🎭 AGENT ACTIVATED: {args.agent.upper()}\n")
        print("=" * 60)
        print(persona)
        print("=" * 60)
        print("\n💡 Copy the persona above and use it as your system prompt!")
    
    elif args.command == "search":
        if not args.agent:
            print("❌ Please specify --agent <search_term>")
            sys.exit(1)
        
        agents = list_agents()
        matches = [a for a in agents if args.agent.lower() in a["name"].lower()]
        
        print(f"🔍 Search results for '{args.agent}':\n")
        for agent in matches:
            print(f"  • {agent['name']} ({agent['category']})")

if __name__ == "__main__":
    main()
