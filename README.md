
# VIBE Sandbox

## Overview
VIBE Sandbox is an open-source project that provides chat-based sandbox malware analysis capabilities. It supports analysis of malware samples in various operating system environments and enables easy integration with other services via the MCP server.

## Architecture
```
[Client (e.g., Cursor)] <---SSE---> [MCP Server] <---Docker/VirtualBox---> [Sandbox VM]
```
- The MCP server (volatility3, virtualbox, etc.) communicates with each sandbox environment and connects to clients via SSE (Server-Sent Events).

## Features
- Chat-based malware analysis
- Sandbox support based on Docker and VirtualBox
- Real-time event streaming via MCP server
- Supports various operating systems (Windows, Linux)
- Memory dump analysis and malware sample execution

## Getting Started
Follow the steps below to install and run VIBE Sandbox:

### Prerequisites
- Python 3.11 or higher
- uv (Python package manager)
- Docker (Windows users need Docker Desktop or WSL2)
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


### Additional Setup
#### OpenBAS Integration
OpenBAS is an open-source BAS (Breach and Attack Simulation) platform that automates real attack scenarios to validate the effectiveness of security solutions. Integrating with VIBE Sandbox offers the following advantages:

- Automatically execute various attack scenarios for analysis in the sandbox environment
- Automate malware sample distribution and execution for efficient repetitive testing
- Real-time integration of OpenBAS events and sandbox analysis results via the MCP server

##### Integration Architecture
```
[OpenBAS] <---API/Script---> [VIBE Sandbox MCP Server] <---Docker/VirtualBox---> [Sandbox VM]
```

##### Example Workflow
1. Select and execute an attack scenario in OpenBAS
2. Use the agent installed in the sandbox VM to deliver and execute commands
3. Analysis results and events are delivered to the client in real time via the MCP server

## Connecting to MCP Server
Once the server is running, you can connect to the MCP server from clients such as Cursor.

### Cursor MCP Configuration Example
Add the `mcp.json` file to Cursor's MCP settings. This file contains the VIBE Sandbox MCP server information:
```json
{
  "mcpServers": {
    "volatility3": {
      "url": "http://localhost:8000/sse/"
    },
    "virtualbox": {
      "url": "http://localhost:9000/sse/"
    }
  }
}
```

## Contribution
This project is open-source. Feel free to leave feedback or contribute via issues and PRs.
