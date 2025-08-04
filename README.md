

# VIBE Sandbox

## Overview
VIBE Sandbox is an open-source, chat-based sandbox for malware analysis across various operating systems. It enables easy integration with other services via the MCP server.

## Architecture
```
[Client (e.g., Cursor)] <---SSE---> [MCP Server] <---Docker/VirtualBox---> [Sandbox VM]
```
- The MCP server (volatility3, virtualbox, etc.) communicates with each sandbox environment and connects to clients via SSE (Server-Sent Events).

## Features
- Chat-based malware analysis
- Sandbox support based on Docker and VirtualBox
- Real-time event streaming via the MCP server
- Supports various operating systems (Windows, Linux)
- Memory dump analysis and malware sample execution

## Getting Started
Follow the steps below to install and run VIBE Sandbox.

### Prerequisites
- Python 3.11 or higher
- uv (Python package manager)
- Docker (Windows users need Docker Desktop)
- VirtualBox

### Installation & Run
1. Clone the repository:
    ```bash
    git clone git@github.com/capelabs/vibe-sandbox.git
    cd vibe-sandbox
    ```
2. Install and sync uv:
    ```bash
    pip install uv
    uv sync
    ```
3. Start the server with Docker Compose:
    ```bash
    docker compose up -d
    ```
4. Start the virtual machine in VirtualBox and run the setup script for your OS:
    - **Windows**: `setup-windows.bat`
    - **Linux**: `setup-linux.sh`

#### Additional Configuration & Tips

- **Running the Volatility3 MCP Server**
  - To run the Volatility3-based MCP server using uv, use the following command:
    ```bash
    uv run --python main.py
    ```
    (Working directory: `volatility3-mcp-server/`)

- **Registering Environment Variables (Windows)**
  - Add the VirtualBox installation path (e.g., `C:\Program Files\Oracle\VirtualBox`) to your system `PATH` environment variable.
  - How to: [Edit system environment variables] → [Environment Variables] → Edit `Path` under System variables → Add the VirtualBox installation path

##### Example Workflow
1. Use the agent installed in the sandbox VM to deliver and execute commands
2. Analysis results and events are delivered to the client in real time via the MCP server

## Connecting to the MCP Server
Once the server is running, you can connect to the MCP server from clients such as Cursor.

### Cursor MCP Configuration Example
Add the `mcp.json` file to Cursor's MCP settings. This file contains the VIBE Sandbox MCP server information:
```json
{
  "mcpServers": {
    "volatility3": {
      "url": "http://localhost:8000/sse"
    },
    "virtualbox": {
      "url": "http://localhost:9000/sse"
    },
    // ...existing code...
  }
}
```

## Contribution
This project is open-source. Feel free to leave feedback or contribute via issues and PRs.
