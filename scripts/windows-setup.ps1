# Function to handle errors and exit
function Exit-OnError {
    param (
        [string]$ErrorMessage
    )
    Write-Host "Error: $ErrorMessage" -ForegroundColor Red
    Write-Host "Script execution terminated due to error." -ForegroundColor Red
    exit 1
}

# Use the provided link to download the Sysmon zip file.

$sysmonUrl = "https://download.sysinternals.com/files/Sysmon.zip"
$sysmonOutputPath = "$env:TEMP\Sysmon.zip"
$sysmonExtractPath = "$env:TEMP\Sysmon"

try {
    Invoke-WebRequest -Uri $sysmonUrl -OutFile $sysmonOutputPath -ErrorAction Stop
    Write-Host "Downloaded Sysmon to $sysmonOutputPath"
} catch {
    Exit-OnError "Failed to download Sysmon. $_"
}

# 2. Unzip sysmon file
# Extract the contents of the downloaded Sysmon zip file to a desired location.

try {
    if (Test-Path $sysmonExtractPath) {
        Remove-Item -Path $sysmonExtractPath -Recurse -Force
    }
    New-Item -Path $sysmonExtractPath -ItemType Directory -Force | Out-Null
    Expand-Archive -Path $sysmonOutputPath -DestinationPath $sysmonExtractPath -Force -ErrorAction Stop
    Write-Host "Extracted Sysmon to $sysmonExtractPath"
} catch {
    Exit-OnError "Failed to extract Sysmon. $_"
}

# Run the Sysmon executable with administrative privileges and accept the EULA.

$sysmonExe = Get-ChildItem -Path $sysmonExtractPath -Filter "Sysmon64.exe" -Recurse | Select-Object -First 1 -ExpandProperty FullName
if (-not $sysmonExe) {
    $sysmonExe = Get-ChildItem -Path $sysmonExtractPath -Filter "Sysmon.exe" -Recurse | Select-Object -First 1 -ExpandProperty FullName
}

if (-not $sysmonExe) {
    Exit-OnError "Sysmon executable not found in the extracted files"
}

# Check if Sysmon is already installed
$sysmonInstalled = Get-Service -Name Sysmon* -ErrorAction SilentlyContinue

# Only install Sysmon if it's not already installed
if (-not $sysmonInstalled) {
    try {
        Write-Host "Installing Sysmon from $sysmonExe"
        $process = Start-Process -FilePath $sysmonExe -ArgumentList "-accepteula", "-i" -Wait -NoNewWindow -PassThru
        if ($process.ExitCode -ne 0) {
            Write-Host "Warning: Sysmon installation failed with exit code: $($process.ExitCode)" -ForegroundColor Yellow
            Write-Host "Continuing with Winlogbeat setup..." -ForegroundColor Yellow
        } else {
            Write-Host "Sysmon installed successfully"
        }
    } catch {
        Write-Host "Warning: Failed to install Sysmon. $_" -ForegroundColor Yellow
        Write-Host "Continuing with Winlogbeat setup..." -ForegroundColor Yellow
    }
} else {
    Write-Host "Sysmon is already installed. Skipping Sysmon installation." -ForegroundColor Yellow
}

# Continue with Winlogbeat setup regardless of Sysmon status
Write-Host "Proceeding with Winlogbeat setup..." -ForegroundColor Green

# Prompt user for Logstash HTTP address
$logstashAddress = Read-Host -Prompt "Enter Logstash HTTP address (e.g. http://logstash-server:8080)"
if ([string]::IsNullOrWhiteSpace($logstashAddress)) {
    $logstashAddress = "10.0.2.2:5044"
    Write-Host "No Logstash address provided. Using default: $logstashAddress" -ForegroundColor Yellow
    $useLogstash = $true
} else {
    # Validate the address format
    if (-not $logstashAddress.StartsWith("http://") -and -not $logstashAddress.StartsWith("https://")) {
        $logstashAddress = "http://" + $logstashAddress
    }
    $useLogstash = $true
    Write-Host "Will configure Winlogbeat to send logs to: $logstashAddress" -ForegroundColor Green
}

# Use the provided link to download the Winlogbeat zip file.


$winlogbeatUrl = "https://artifacts.elastic.co/downloads/beats/winlogbeat/winlogbeat-9.0.3-windows-x86_64.zip"
$winlogbeatOutputPath = "$env:TEMP\winlogbeat.zip"
$winlogbeatExtractPath = "C:\Program Files\Winlogbeat"

if (Test-Path $winlogbeatExtractPath) {
    Write-Host "Winlogbeat already exists at $winlogbeatExtractPath. Skipping download and extraction." -ForegroundColor Yellow
} else {
    try {
        Invoke-WebRequest -Uri $winlogbeatUrl -OutFile $winlogbeatOutputPath -ErrorAction Stop
        Write-Host "Downloaded Winlogbeat to $winlogbeatOutputPath"
    } catch {
        Exit-OnError "Failed to download Winlogbeat. $_"
    }

    # Extract the contents of the downloaded Winlogbeat zip file to a desired location.
    try {
        if (Test-Path $winlogbeatExtractPath) {
            Remove-Item -Path $winlogbeatExtractPath -Recurse -Force
        }
        New-Item -Path $winlogbeatExtractPath -ItemType Directory -Force | Out-Null
        Expand-Archive -Path $winlogbeatOutputPath -DestinationPath $winlogbeatExtractPath -Force -ErrorAction Stop
        Write-Host "Extracted Winlogbeat to $winlogbeatExtractPath"

        # Fix directory structure (zip contains an inner directory)
        $innerDir = Get-ChildItem -Path $winlogbeatExtractPath -Directory | Select-Object -First 1
        if ($innerDir) {
            Get-ChildItem -Path $innerDir.FullName | Copy-Item -Destination $winlogbeatExtractPath -Recurse -Force
            Remove-Item -Path $innerDir.FullName -Recurse -Force
        }
    } catch {
        Exit-OnError "Failed to extract Winlogbeat. $_"
    }
}

# Modify the Winlogbeat configuration file (winlogbeat.yml) to specify log sources and output settings.

$winlogbeatConfigPath = Join-Path -Path $winlogbeatExtractPath -ChildPath "winlogbeat.yml"

if (-not (Test-Path $winlogbeatConfigPath)) {
    Exit-OnError "Winlogbeat configuration file not found at $winlogbeatConfigPath"
}

try {
    # Backup the original configuration
    Copy-Item -Path $winlogbeatConfigPath -Destination "$winlogbeatConfigPath.bak" -Force
    
    # Create configuration based on user's choice of output
    if ($useLogstash) {
        $winlogbeatConfig = @"
winlogbeat.event_logs:
  - name: Microsoft-Windows-Sysmon/Operational

# Output to Logstash HTTP endpoint
output.logstash:
  hosts: ["$logstashAddress"]
  
# Disable SSL verification if using http
ssl.verification_mode: none

logging.level: info
logging.to_files: true
logging.files:
  path: C:/ProgramData/winlogbeat/Logs
  name: winlogbeat.log
  keepfiles: 7
  permissions: 0644
"@
        Write-Host "Winlogbeat configured to send logs to Logstash at $logstashAddress"
    } else {
        $winlogbeatConfig = @"
winlogbeat.event_logs:
  - name: Microsoft-Windows-Sysmon/Operational

# Output to files
output.file:
  path: "C:/ProgramData/winlogbeat/output"
  filename: winlogbeat
  rotate_every_kb: 10000
  number_of_files: 7

logging.level: info
logging.to_files: true
logging.files:
  path: C:/ProgramData/winlogbeat/Logs
  name: winlogbeat.log
  keepfiles: 7
  permissions: 0644
"@
        
        # Create output directory if it doesn't exist
        $outputDir = "C:/ProgramData/winlogbeat/output"
        if (-not (Test-Path $outputDir)) {
            New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
        }
        
        Write-Host "Winlogbeat configuration updated to use file output at $outputDir"
    }

    # Write the new configuration
    Set-Content -Path $winlogbeatConfigPath -Value $winlogbeatConfig -ErrorAction Stop
    
} catch {
    Exit-OnError "Failed to configure Winlogbeat. $_"
}

# Run the PowerShell script to install Winlogbeat as a Windows service

$installScriptPath = Join-Path -Path $winlogbeatExtractPath -ChildPath "install-service-winlogbeat.ps1"
if (-not (Test-Path $installScriptPath)) {
    # Try alternative locations as fallback
    $possiblePaths = @(
        "$winlogbeatExtractPath\install-script-winlogbeat.ps1",
        "$winlogbeatExtractPath\scripts\install-service-winlogbeat.ps1"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $installScriptPath = $path
            break
        }
    }
}

try {
    Write-Host "Installing Winlogbeat service"
    # Set execution policy to allow script execution
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
    
    # Execute the installation script
    & $installScriptPath
    
    # Start the service
    Start-Service winlogbeat
    Write-Host "Winlogbeat service installed and started"
} catch {
    Exit-OnError "Failed to install or start Winlogbeat service. $_"
}

Write-Host "Setup completed successfully" -ForegroundColor Green
