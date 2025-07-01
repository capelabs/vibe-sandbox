from fastmcp import FastMCP

import subprocess


mcp = FastMCP(name="VirtualBox MCP Server")


def run_vboxmanage_command(command: str):
    """
    Execute VBoxManage command and return the result.
    :param command: VBoxManage command to execute
    :return: Command execution result
    """

    try:
        result = subprocess.run(
            ["VBoxManage"] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}


@mcp.tool
async def get_all_vms():
    """
    Get information about all VirtualBox VMs.
    :return: List of VM information
    """
    command = "list vms"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    vms = []
    for line in output.splitlines():
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
    command = f"showvminfo {vm_id} --machinereadable"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    vm_info = {}
    for line in output.splitlines():
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
    command = f"startvm {vm_id} --type headless"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    return {"message": f"VM {vm_id} has been started successfully."}


@mcp.tool
async def stop_vm(vm_id: str):
    """
    Stop a specific VM.
    :param vm_id: VM ID
    :return: Stop result message
    """
    command = f"controlvm {vm_id} poweroff"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    return {"message": f"VM {vm_id} has been stopped successfully."}


@mcp.tool
async def import_vm_from_ova(ova_path: str):
    """
    Import a VM from an OVA file.
    :param ova_path: OVA file path
    :return: Import result message
    """
    command = f"import {ova_path}"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    return {"message": f"VM has been imported from {ova_path} successfully."}


@mcp.tool
async def extract_memory_dump_from_vm(vm_id: str, dump_path: str):
    """
    Extract a memory dump from a specific VM.
    :param vm_id: VM ID
    :param dump_path: Path to save the dump file
    :return: Extraction result message
    """
    command = f"debugvm {vm_id} dumpvmcore --filename={dump_path}"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    return {"message": f"Memory dump for VM {vm_id} has been saved to {dump_path}."}


@mcp.tool
async def copy_file_to_vm(vm_id: str, host_path: str, vm_path: str):
    """
    Copy a file from the host to a VM.
    :param vm_id: VM ID
    :param host_path: Host file path
    :param vm_path: Destination path in the VM
    :return: Copy result message
    """
    command = f"guestcontrol {vm_id} copyto {host_path} --target-directory={vm_path}"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    return {"message": f"File {host_path} has been copied to VM {vm_id} at {vm_path}."}


@mcp.tool
async def execute_command_in_vm(vm_id: str, exe: str, command: str):
    """
    Execute a command in a VM.
    :param vm_id: VM ID
    :param exe: Path to executable
    :param command: Command to execute
    :return: Execution result message
    """
    command = f"guestcontrol {vm_id} run --exe {exe} -- -c '{command}'"
    output = run_vboxmanage_command(command)
    
    if "error" in output:
        return {"error": output}
    
    return {"message": f"Command executed in VM {vm_id}: {command}", "output": output}


if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=9000,
    )
