

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
2. Install and sync uv (for virtualbox-mcp-server):
    ```bash
    pip install uv
    cd virtualbox-mcp-server
    uv sync
    ```
3. Start the server with Docker Compose:
    ```bash
    docker compose up -d
    ```
4. Start the virtual machine in VirtualBox and run the setup script for your OS with Administrator privileges:
    - **Windows**: `setup-windows.bat`
    - **Linux**: `setup-linux.sh`

    > **Note:**
    > When prompted for the logstash address during setup, use `10.0.2.2:5044` (for Windows) or `http://10.0.2.2:5045` (for Linux). This allows the VM to communicate with the logstash service running on the host machine.

#### Additional Configuration & Tips

- **Running the Virtualbox MCP Server**
  - To run the Virtualbox-based MCP server using uv, use the following command:
    ```bash
    uv run python main.py
    ```
    (Working directory: `virtualbox-mcp-server/`)

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
    "opensearch": {
      "url": "http://localhost:9200/_plugins/_ml/mcp/sse?append_to_base_url=true",
      "headers": {
        "Content-Type": "application/json",
        "Accept-Encoding": "identity"
      }
    }
  }
}
```

## Contribution
This project is open-source. Feel free to leave feedback or contribute via issues and PRs.
