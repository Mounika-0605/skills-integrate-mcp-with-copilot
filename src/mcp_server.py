#!/usr/bin/env python3
"""
MCP Server for Extracurricular Activities Management

This server exposes tools that allow Copilot to interact with the activities
management system, enabling querying and managing student registrations.
"""

import json
from pathlib import Path
from typing import Any
import subprocess
import sys

# Import MCP SDK components
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

# Initialize the MCP server
server = Server("activities-management")

# Load activities and teachers data
current_dir = Path(__file__).parent

def load_activities():
    """Load activities from JSON file"""
    with open(current_dir / "activities.json", "r") as f:
        return json.load(f)

def load_teachers():
    """Load teachers from JSON file"""
    with open(current_dir / "teachers.json", "r") as f:
        return json.load(f)

def save_activities(activities: dict):
    """Save activities to JSON file"""
    with open(current_dir / "activities.json", "w") as f:
        json.dump(activities, f, indent=2)


# Define MCP Tools
@server.call_tool()
def handle_tool_call(name: str, arguments: dict) -> Any:
    """Handle tool calls from Copilot"""
    
    if name == "list_activities":
        return handle_list_activities()
    elif name == "get_activity_details":
        return handle_get_activity_details(arguments)
    elif name == "signup_student":
        return handle_signup_student(arguments)
    elif name == "list_participants":
        return handle_list_participants(arguments)
    elif name == "get_activity_stats":
        return handle_get_activity_stats()
    else:
        return ToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])


def handle_list_activities() -> ToolResult:
    """List all available activities"""
    activities = load_activities()
    activity_list = []
    
    for name, details in activities.items():
        activity_list.append(f"- {name}: {details.get('description', 'No description')}")
    
    content = "\n".join(activity_list) if activity_list else "No activities found"
    return ToolResult(content=[TextContent(type="text", text=content)])


def handle_get_activity_details(arguments: dict) -> ToolResult:
    """Get detailed information about a specific activity"""
    activity_name = arguments.get("activity_name")
    activities = load_activities()
    
    if activity_name not in activities:
        return ToolResult(content=[TextContent(type="text", text=f"Activity '{activity_name}' not found")])
    
    activity = activities[activity_name]
    details = f"""
Activity: {activity_name}
Description: {activity.get('description', 'N/A')}
Coach: {activity.get('coach', 'N/A')}
Location: {activity.get('location', 'N/A')}
Meeting Time: {activity.get('meeting_time', 'N/A')}
Current Participants: {len(activity.get('participants', []))}
Max Capacity: {activity.get('max_capacity', 'Unlimited')}
"""
    return ToolResult(content=[TextContent(type="text", text=details.strip())])


def handle_signup_student(arguments: dict) -> ToolResult:
    """Sign up a student for an activity"""
    activity_name = arguments.get("activity_name")
    email = arguments.get("email")
    
    activities = load_activities()
    
    if activity_name not in activities:
        return ToolResult(content=[TextContent(type="text", text=f"Activity '{activity_name}' not found")])
    
    activity = activities[activity_name]
    
    if email in activity.get("participants", []):
        return ToolResult(content=[TextContent(type="text", text=f"Student {email} is already registered for {activity_name}")])
    
    activity.setdefault("participants", []).append(email)
    save_activities(activities)
    
    return ToolResult(content=[TextContent(type="text", text=f"Successfully signed up {email} for {activity_name}")])


def handle_list_participants(arguments: dict) -> ToolResult:
    """List all participants in an activity"""
    activity_name = arguments.get("activity_name")
    activities = load_activities()
    
    if activity_name not in activities:
        return ToolResult(content=[TextContent(type="text", text=f"Activity '{activity_name}' not found")])
    
    participants = activities[activity_name].get("participants", [])
    
    if not participants:
        return ToolResult(content=[TextContent(type="text", text=f"No participants in {activity_name}")])
    
    participant_list = "\n".join([f"- {p}" for p in participants])
    return ToolResult(content=[TextContent(type="text", text=f"Participants in {activity_name}:\n{participant_list}")])


def handle_get_activity_stats() -> ToolResult:
    """Get statistics about all activities"""
    activities = load_activities()
    
    total_activities = len(activities)
    total_registrations = sum(len(a.get("participants", [])) for a in activities.values())
    
    stats = f"""
Activity Statistics:
- Total Activities: {total_activities}
- Total Registrations: {total_registrations}

Activities Breakdown:
"""
    
    for name, activity in activities.items():
        count = len(activity.get("participants", []))
        stats += f"\n- {name}: {count} participants"
    
    return ToolResult(content=[TextContent(type="text", text=stats.strip())])


# Register tools with MCP
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for Copilot"""
    return [
        Tool(
            name="list_activities",
            description="List all available extracurricular activities",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_activity_details",
            description="Get detailed information about a specific activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_name": {
                        "type": "string",
                        "description": "The name of the activity"
                    }
                },
                "required": ["activity_name"]
            }
        ),
        Tool(
            name="signup_student",
            description="Sign up a student for an activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_name": {
                        "type": "string",
                        "description": "The name of the activity"
                    },
                    "email": {
                        "type": "string",
                        "description": "Student email address"
                    }
                },
                "required": ["activity_name", "email"]
            }
        ),
        Tool(
            name="list_participants",
            description="List all participants in a specific activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_name": {
                        "type": "string",
                        "description": "The name of the activity"
                    }
                },
                "required": ["activity_name"]
            }
        ),
        Tool(
            name="get_activity_stats",
            description="Get statistics about all activities and registrations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


if __name__ == "__main__":
    # Use the MCP's start server implementation
    import asyncio
    asyncio.run(server.run(sys.stdin.buffer, sys.stdout.buffer))
