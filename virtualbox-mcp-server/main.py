from fastmcp import FastMCP

import subprocess


mcp = FastMCP(name="VirtualBox MCP Server")


def run_vboxmanage_command(commands: list[str], auth: dict = None):
    """
    Execute VBoxManage command and return the result.
    :param commands: VBoxManage commands to execute
    :param auth: authentication parameters {"username": "user", "password": "pass"}
    :return: Command execution result
    """

    if auth:
        # If authentication is provided, add it to the command
        commands = commands + ["--username", auth.get("username", ""), "--password", auth.get("password", "")]

    try:
        result = subprocess.Popen(
            ' '.join(["VBoxManage", "--nologo"] + commands),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return {
            "stdout": result.stdout.read().decode('utf-8').strip(),
            "stderr": result.stderr.read().decode('utf-8').strip()
        }
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}


@mcp.tool
async def get_all_vms():
    """
    Get information about all VirtualBox VMs.
    :return: List of VM information
    """
    output = run_vboxmanage_command(["list", "vms"])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"]}
    
    vms = []
    for line in output["stdout"].splitlines():
        parts = line.split('"')
        if len(parts) >= 3:
            vm_name = parts[1]
            vm_id = parts[2].strip()
            vms.append({"name": vm_name, "id": vm_id})
    
    return vms


@mcp.tool
async def get_vm_info(vm_id: str):
    """
    Get information about a specific VM.
    :param vm_id: VM ID
    :return: VM information
    """
    output = run_vboxmanage_command(["showvminfo", vm_id, "--machinereadable"])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"]}
    
    vm_info = {}
    for line in output["stdout"].splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            vm_info[key.strip()] = value.strip().strip('"')
    
    return vm_info


@mcp.tool
async def start_vm(vm_id: str):
    """
    Start a specific VM.
    :param vm_id: VM ID
    :return: Start result message
    """
    output = run_vboxmanage_command(["startvm", vm_id, "--type", "headless"])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"VM {vm_id} has been started successfully.", "stdout": output.get("stdout", "")}


@mcp.tool
async def stop_vm(vm_id: str):
    """
    Stop a specific VM.
    :param vm_id: VM ID
    :return: Stop result message
    """
    output = run_vboxmanage_command(["controlvm", vm_id, "poweroff"])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"VM {vm_id} has been stopped successfully.", "stdout": output.get("stdout", "")}


@mcp.tool
async def import_vm_from_ova(ova_path: str):
    """
    Import a VM from an OVA file.
    :param ova_path: OVA file path
    :return: Import result message
    """
    output = run_vboxmanage_command(["import", ova_path])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"VM has been imported from {ova_path} successfully.", "stdout": output.get("stdout", "")}


@mcp.tool
async def extract_memory_dump_from_vm(vm_id: str, dump_path: str):
    """
    Extract a memory dump from a specific VM.
    :param vm_id: VM ID
    :param dump_path: Path to save the dump file
    :return: Extraction result message
    """
    output = run_vboxmanage_command(["debugvm", vm_id, "dumpvmcore", f"--filename={dump_path}"])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"Memory dump for VM {vm_id} has been saved to {dump_path}.", "stdout": output.get("stdout", "")}


@mcp.tool
async def copy_file_to_vm(vm_id: str, host_path: str, vm_path: str, auth: dict = None):
    """
    Copy a file from the host to a VM.
    :param vm_id: VM ID
    :param host_path: Host file path
    :param vm_path: Destination path in the VM
    :param auth: authentication parameters {"username": "user", "password": "pass"}
    :return: Copy result message
    """
    output = run_vboxmanage_command([
        "guestcontrol", vm_id, "copyto",
        host_path, f"--target-directory={vm_path}",
        f"--username={auth.get('username', '')}", f"--password={auth.get('password', '')}"
    ])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"File {host_path} has been copied to VM {vm_id} at {vm_path}.", "stdout": output.get("stdout", "")}


@mcp.tool
async def execute_command_in_vm(vm_id: str, exe: str, command: str, auth: dict = None):
    """
    Execute a command in a VM.
    :param vm_id: VM ID
    :param exe: Path to executable
    :param command: Command to execute
    :param auth: authentication parameters {"username": "user", "password": "pass"}
    :return: Execution result message
    """
    output = run_vboxmanage_command([
        "guestcontrol", vm_id, "run",
        f"--username={auth.get("username", "")}", f"--password={auth.get("password", "")}",
        "--", exe, command
    ])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"Command executed in VM {vm_id}: {command}", "output": output}


@mcp.tool
async def rename_file_in_vm(vm_id: str, old_name: str, new_name: str, auth: dict = None):
    """
    Rename a file in a VM.
    :param vm_id: VM ID
    :param old_name: Current file name
    :param new_name: New file name
    :param auth: authentication parameters {"username": "user", "password": "pass"}
    :return: Rename result message
    """
    output = run_vboxmanage_command([
        "guestcontrol", vm_id, "mv",
        f"--username={auth.get('username', '')}", f"--password={auth.get('password', '')}",
        old_name, new_name
    ])
    
    if "error" in output:
        return {"error": output["error"]}
    
    if output.get("stderr"):
        return {"error": output["stderr"], "stdout": output.get("stdout", "")}
    
    return {"message": f"File {old_name} has been renamed to {new_name} in VM {vm_id}.", "stdout": output.get("stdout", "")}



if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=9000,
    )
