<#
.SYNOPSIS
    Reorganizes the WorkoutAgents project directory structure.

.DESCRIPTION
    This script reorganizes the WorkoutAgents project by:
    1. Creating a new backend/ folder
    2. Moving all backend-specific files and folders to the backend/ folder
    3. Creating a new frontend/ folder
    4. Cloning the agile-fitness-agent-pwa repository into the frontend/ folder

.NOTES
    Author: Claude
    Date: June 1, 2025
    Version: 1.0
    
    IMPORTANT: This script will move files and folders. It is highly recommended
    to create a backup of your project before running this script.
#>

# Stop on first error
$ErrorActionPreference = "Stop"

# Base directory path
$baseDir = "C:\Users\adonath\Documents\WorkoutAgents"

# New directory paths
$backendDir = Join-Path -Path $baseDir -ChildPath "backend"
$frontendDir = Join-Path -Path $baseDir -ChildPath "frontend"

# Function to display colored output messages
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Function to check if a command exists
function Test-CommandExists {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Command
    )
    
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    return $exists
}

# Function to create a backup recommendation
function Show-BackupRecommendation {
    Write-ColorOutput "`n===== BACKUP RECOMMENDATION =====" "Yellow"
    Write-ColorOutput "It is STRONGLY recommended to create a backup of your project before proceeding." "Yellow"
    Write-ColorOutput "You can create a backup by running:" "Yellow"
    Write-ColorOutput "    Copy-Item -Path '$baseDir' -Destination '$baseDir-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')' -Recurse" "Cyan"
    Write-ColorOutput "===== END RECOMMENDATION =====`n" "Yellow"
    
    $response = Read-Host "Would you like to create a backup now? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        $backupDir = "$baseDir-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-ColorOutput "Creating backup at $backupDir..." "Green"
        try {
            Copy-Item -Path $baseDir -Destination $backupDir -Recurse
            Write-ColorOutput "Backup created successfully!" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to create backup: ${errorMsg}" "Red"
            Write-ColorOutput "Please create a manual backup before proceeding." "Red"
            exit 1
        }
    }
    else {
        Write-ColorOutput "Proceeding without backup. Be cautious!" "Yellow"
    }
}

# Function to check prerequisites
function Check-Prerequisites {
    Write-ColorOutput "Checking prerequisites..." "Blue"
    
    # Check if Git is installed
    if (-not (Test-CommandExists "git")) {
        Write-ColorOutput "Git is not installed. Please install Git before running this script." "Red"
        exit 1
    }
    
    # Check if base directory exists
    if (-not (Test-Path -Path $baseDir)) {
        Write-ColorOutput "Base directory '$baseDir' does not exist." "Red"
        exit 1
    }
    
    # Check if new directories already exist
    if (Test-Path -Path $backendDir) {
        Write-ColorOutput "Backend directory '$backendDir' already exists." "Yellow"
        $response = Read-Host "Would you like to continue and use the existing directory? (Y/N)"
        if ($response -ne "Y" -and $response -ne "y") {
            Write-ColorOutput "Operation cancelled by user." "Yellow"
            exit 0
        }
    }
    
    if (Test-Path -Path $frontendDir) {
        Write-ColorOutput "Frontend directory '$frontendDir' already exists." "Yellow"
        $response = Read-Host "Would you like to continue and use the existing directory? (Y/N)"
        if ($response -ne "Y" -and $response -ne "y") {
            Write-ColorOutput "Operation cancelled by user." "Yellow"
            exit 0
        }
    }
    
    Write-ColorOutput "All prerequisites checked." "Green"
}

# Function to create directories
function Create-Directories {
    Write-ColorOutput "Creating directories..." "Blue"
    
    # Create backend directory if it doesn't exist
    if (-not (Test-Path -Path $backendDir)) {
        try {
            New-Item -Path $backendDir -ItemType Directory | Out-Null
            Write-ColorOutput "Created backend directory: $backendDir" "Green"
        }
        catch {
            Write-ColorOutput "Failed to create backend directory: ${_}" "Red"
            exit 1
        }
    }
    
    # Create frontend directory if it doesn't exist
    if (-not (Test-Path -Path $frontendDir)) {
        try {
            New-Item -Path $frontendDir -ItemType Directory | Out-Null
            Write-ColorOutput "Created frontend directory: $frontendDir" "Green"
        }
        catch {
            Write-ColorOutput "Failed to create frontend directory: ${_}" "Red"
            exit 1
        }
    }
    
    Write-ColorOutput "Directories created successfully." "Green"
}

# Function to move backend files and folders
function Move-BackendFiles {
    Write-ColorOutput "Moving backend files and folders..." "Blue"
    
    # List of specific files to move
    $specificFiles = @(
        "validation_agent_langchain.py",
        "training_agent_mike.py",
        "tracking_agent_trystero.py",
        "agent_tools.py",
        "main.py",
        "requirements.txt",
        ".env",
        ".env.example",
        ".gitignore"
    )
    
    # Move specific files
    foreach ($file in $specificFiles) {
        $sourcePath = Join-Path -Path $baseDir -ChildPath $file
        $destinationPath = Join-Path -Path $backendDir -ChildPath $file
        
        if (Test-Path -Path $sourcePath) {
            try {
                Move-Item -Path $sourcePath -Destination $destinationPath -Force
                Write-ColorOutput "Moved file: $file" "Green"
            }
            catch {
                $errorMsg = $_.Exception.Message
                Write-ColorOutput "Failed to move file ${file}: ${errorMsg}" "Red"
            }
        }
        else {
            Write-ColorOutput "File not found: $file" "Yellow"
        }
    }
    
    # Move app folder
    $appSourcePath = Join-Path -Path $baseDir -ChildPath "app"
    $appDestinationPath = Join-Path -Path $backendDir -ChildPath "app"
    
    if (Test-Path -Path $appSourcePath) {
        try {
            Move-Item -Path $appSourcePath -Destination $appDestinationPath -Force
            Write-ColorOutput "Moved folder: app/" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move app/ folder: ${errorMsg}" "Red"
        }
    }
    else {
        Write-ColorOutput "Folder not found: app/" "Yellow"
    }
    
    # Move venv folder if it exists
    $venvSourcePath = Join-Path -Path $baseDir -ChildPath "venv"
    $venvDestinationPath = Join-Path -Path $backendDir -ChildPath "venv"
    
    if (Test-Path -Path $venvSourcePath) {
        try {
            Move-Item -Path $venvSourcePath -Destination $venvDestinationPath -Force
            Write-ColorOutput "Moved folder: venv/" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move venv/ folder: ${errorMsg}" "Red"
        }
    }
    else {
        Write-ColorOutput "Folder not found: venv/" "Yellow"
    }
    
    # Move all Python files
    Get-ChildItem -Path $baseDir -Filter "*.py" | ForEach-Object {
        try {
            $fileName = $_.Name
            $destinationPath = Join-Path -Path $backendDir -ChildPath $fileName
            Move-Item -Path $_.FullName -Destination $destinationPath -Force
            Write-ColorOutput "Moved Python file: $fileName" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move Python file ${fileName}: ${errorMsg}" "Red"
        }
    }
    
    # Move all Markdown files
    Get-ChildItem -Path $baseDir -Filter "*.md" | ForEach-Object {
        try {
            $fileName = $_.Name
            $destinationPath = Join-Path -Path $backendDir -ChildPath $fileName
            Move-Item -Path $_.FullName -Destination $destinationPath -Force
            Write-ColorOutput "Moved Markdown file: $fileName" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move Markdown file ${fileName}: ${errorMsg}" "Red"
        }
    }
    
    # Move all test files
    Get-ChildItem -Path $baseDir -Filter "test_*.py" | ForEach-Object {
        try {
            $fileName = $_.Name
            $destinationPath = Join-Path -Path $backendDir -ChildPath $fileName
            # Skip if already moved by the Python files loop
            if (Test-Path -Path $_.FullName) {
                Move-Item -Path $_.FullName -Destination $destinationPath -Force
                Write-ColorOutput "Moved test file: $fileName" "Green"
            }
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move test file ${fileName}: ${errorMsg}" "Red"
        }
    }
    
    # Move any remaining audio files that might be related to the backend
    Get-ChildItem -Path $baseDir -Filter "*.mp3" | ForEach-Object {
        try {
            $fileName = $_.Name
            $destinationPath = Join-Path -Path $backendDir -ChildPath $fileName
            Move-Item -Path $_.FullName -Destination $destinationPath -Force
            Write-ColorOutput "Moved audio file: $fileName" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move audio file ${fileName}: ${errorMsg}" "Red"
        }
    }
    
    # Move log files
    Get-ChildItem -Path $baseDir -Filter "*.log" | ForEach-Object {
        try {
            $fileName = $_.Name
            $destinationPath = Join-Path -Path $backendDir -ChildPath $fileName
            Move-Item -Path $_.FullName -Destination $destinationPath -Force
            Write-ColorOutput "Moved log file: $fileName" "Green"
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-ColorOutput "Failed to move log file ${fileName}: ${errorMsg}" "Red"
        }
    }
    
    Write-ColorOutput "Backend files and folders moved successfully." "Green"
}

# Function to clone frontend repository
function Clone-FrontendRepository {
    Write-ColorOutput "Cloning frontend repository..." "Blue"
    
    $repoUrl = "https://github.com/derkaal/agile-fitness-agent-pwa.git"
    
    try {
        # Change to the frontend directory
        Set-Location -Path $frontendDir
        
        # Clone the repository
        $output = git clone $repoUrl .
        
        Write-ColorOutput "Frontend repository cloned successfully." "Green"
    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-ColorOutput "Failed to clone frontend repository: ${errorMsg}" "Red"
        exit 1
    }
    finally {
        # Return to the base directory
        Set-Location -Path $baseDir
    }
}

# Main execution
try {
    Write-ColorOutput "=== WorkoutAgents Project Reorganization Script ===" "Cyan"
    Write-ColorOutput "This script will reorganize your project according to the specified requirements." "White"
    
    # Show backup recommendation
    Show-BackupRecommendation
    
    # Check prerequisites
    Check-Prerequisites
    
    # Create directories
    Create-Directories
    
    # Move backend files and folders
    Move-BackendFiles
    
    # Clone frontend repository
    Clone-FrontendRepository
    
    Write-ColorOutput "`n=== Project Reorganization Complete ===" "Cyan"
    Write-ColorOutput "Your project has been successfully reorganized with the following structure:" "White"
    Write-ColorOutput "- $baseDir" "White"
    Write-ColorOutput "  |- backend/" "White"
    Write-ColorOutput "  |  |- app/" "White"
    Write-ColorOutput "  |  |- venv/ (if it existed)" "White"
    Write-ColorOutput "  |  |- Python files (.py)" "White"
    Write-ColorOutput "  |  |- Markdown files (.md)" "White"
    Write-ColorOutput "  |  |- Configuration files (.env, .gitignore)" "White"
    Write-ColorOutput "  |  |- Other backend-related files" "White"
    Write-ColorOutput "  |- frontend/" "White"
    Write-ColorOutput "     |- Files from agile-fitness-agent-pwa repository" "White"
    
    Write-ColorOutput "`nNOTE: You may need to update any paths in your code or configuration files" "Yellow"
    Write-ColorOutput "      to reflect the new directory structure." "Yellow"
}
catch {
    $errorMsg = $_.Exception.Message
    Write-ColorOutput "An unexpected error occurred: ${errorMsg}" "Red"
    Write-ColorOutput "Project reorganization failed. Please check the error message and try again." "Red"
    exit 1
}