# MCP Server Configuration for VS Code

To integrate this MCP server with GitHub Copilot in VS Code, add the following configuration to your VS Code settings or use the MCP configuration format.

## VS Code Settings Configuration

Add this to your `.vscode/settings.json`:

```json
{
  "github.copilot.enable": {
    "*": true
  },
  "mcpServers": {
    "activities-management": {
      "command": "python",
      "args": [
        "src/mcp_server.py"
      ],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## Claude/Cursor Configuration

If you're using Claude or Cursor IDE, add this to your configuration:

```json
{
  "mcpServers": {
    "activities-management": {
      "command": "python",
      "args": [
        "${workspaceFolder}/src/mcp_server.py"
      ]
    }
  }
}
```

## Available Tools

The MCP server exposes the following tools to Copilot:

1. **list_activities** - List all available extracurricular activities
2. **get_activity_details** - Get detailed information about a specific activity
3. **signup_student** - Sign up a student for an activity
4. **list_participants** - List all participants in a specific activity
5. **get_activity_stats** - Get statistics about all activities

## Usage Example

Once configured, you can ask Copilot questions like:

- "What extracurricular activities are available?"
- "Tell me about the chess club"
- "How many students are registered for sports?"
- "Sign up john@school.com for robotics club"

## Running the Server

To start the MCP server manually for testing:

```bash
cd src
python mcp_server.py
```

## Requirements

Make sure you have the MCP SDK installed:

```bash
pip install mcp
```
