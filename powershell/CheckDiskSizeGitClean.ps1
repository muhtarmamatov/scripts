$diskFreeSpaceLimit = 50  # Disk free space limit in gigabytes (50GB)
$diskFreeSpace = (Get-PSDrive -Name 'C').Free / 1GB
$PATH_CLEAN = "C:\TeamCityBuildAgent\work"

if ($diskFreeSpace -lt $diskFreeSpaceLimit) {
    $workFolderPath = $PATH_CLEAN

    # Get a list of subfolders in the work folder
    $subFolders = Get-ChildItem -Path $workFolderPath -Directory

    foreach ($subFolder in $subFolders) {
        $subFolderPath = $subFolder.FullName

        # Check if the subfolder is a Git repository
        $isGitRepo = Test-Path (Join-Path -Path $subFolderPath -ChildPath ".git") -PathType Container

        if ($isGitRepo) {
            # Change to the subfolder
            Set-Location -Path $subFolderPath

            # Run git clean command
            Write-Host "Running git clean in $subFolderPath"
            git clean -x -f -d
        }
    }
}
