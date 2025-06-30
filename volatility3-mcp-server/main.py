from fastmcp import FastMCP

import volatility3
import volatility3.plugins
from volatility3 import framework

import subprocess
import os


mcp = FastMCP(name="Volatility3 MCP Server")

framework.import_files(volatility3.plugins, True)
memory_dumps_path = os.getenv("VOLATILITY_MEMORY_DUMPS_PATH", "dumps")


def run_volatility_plugin(plugin_name, memory_dump, arguments):
    """Run a Volatility plugin on a specified memory dump.

    Args:
        plugin_name (str): The name of the Volatility plugin to run.
        memory_dump (str): The name of the memory dump file to analyze.
        arguments (str): Additional arguments for the plugin.

    Returns:
        dict: The results of the plugin execution.
    """
    if not os.path.isfile(os.path.join(memory_dumps_path, memory_dump)):
        raise FileNotFoundError(f"Memory dump '{memory_dump}' not found in '{memory_dumps_path}'.")

    command = [
        "volatility",
        "-f", os.path.join(memory_dumps_path, memory_dump),
        "-r", "json",
        plugin_name,
    ]

    if arguments:
        command.append(arguments)

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"output": e.stdout, "error": e.stderr}


@mcp.tool()
def run_plugin(plugin_name, memory_dump, arguments):
    """Run a specified Volatility plugin on a memory dump.

    Args:
        plugin_name (str): The name of the Volatility plugin to run.
        memory_dump (str): The name of the memory dump file to analyze.
        arguments (str): Additional arguments for the plugin.

    Returns:
        dict: The output and error messages from the plugin execution.
    """
    return run_volatility_plugin(plugin_name, memory_dump, arguments)


@mcp.tool()
def list_memory_dumps():
    """List all available memory dumps.

    Returns:
        dict: A dictionary containing the names of available memory dumps.
    """
    if not os.path.isdir(memory_dumps_path):
        os.makedirs(memory_dumps_path)
        return {"dumps": []}
    
    dumps = [f for f in os.listdir(memory_dumps_path)]
    return {"dumps": dumps}


@mcp.tool()
async def list_all_available_plugins():
    """Retrieve a list of all available Volatility plugins.

    Returns:
        dict: A dictionary containing the names and descriptions of all plugins.
    """
    plugins = framework.list_plugins()
    return {
        "plugins": [
            dict(name=name, description=plugins[name].__doc__)
            for name in plugins.keys()
        ],
    }


if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8000,
    )
