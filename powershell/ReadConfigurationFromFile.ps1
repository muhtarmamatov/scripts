function ReadConfigFile($filePath) {
    <#
    This function reads a configuration file and extracts key-value pairs.

    Parameters:
    - $filePath (string): The path to the configuration file.

    Returns:
    - Hashtable: A hashtable containing the key-value pairs from the configuration file.
    #>

    try {
        # Check if the file exists
        if (-not (Test-Path $filePath)) {
            throw "Configuration file not found. Please correct config path: $filePath"
        }

        # Read the file content
        $fileContent = Get-Content $filePath

        # Initialize an empty hashtable
        $configData = @{}

        # Process each line in the file
        foreach ($line in $fileContent) {
            # Skip empty lines and comments
            if (-not [string]::IsNullOrWhiteSpace($line) -and -not $line.StartsWith("#")) {
                # Split the line into key and value
                $key, $value = $line -split "=", 2

                # Trim leading/trailing whitespace from the key and value
                $key = $key.Trim()
                $value = $value.Trim()

                # Add the key-value pair to the hashtable
                $configData[$key] = $value
            }
        }

        # Return the hashtable
        return $configData
    }
    catch {
        # Log the error
        Write-Host "Error: $_"
        return @{}
    }
}

# Example usage
$filePath = ".\financesoft\config\script_configuration.txt"
$configData = ReadConfigFile $filePath

# Access the values using the keys
$workDir = $configData["WorkDIR"]
$nunit3Path = $configData["Nunit3Path"]
$projectPath = $configData["ProjectPath"]


Write-Output($workDir)
Write-Output($nunit3Path)
Write-Output($projectPath)

$paths =@("$workDir", "$nunit3Path", "$projectPath")
