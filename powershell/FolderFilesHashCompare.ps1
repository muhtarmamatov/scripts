Write-Host "========================================================================================" -ForegroundColor Green
Write-Host "======================================== FOLDER HASH COMPARE SHELL =====================" -ForegroundColor Green
Write-Host "========================================================================================" -ForegroundColor Green

function main{
    Write-Host "==================================== SELECT SOURCE FOLDER  ==========================" -ForegroundColor Green
    $srcFolder = SelectFolder

    Write-Host "================================== SELECT DESTINATION FOLDER =========================" -ForegroundColor Green
    $destFolder = SelectFolder

    Write-Host "================================== LOADING FILE HASHES ================================" -ForegroundColor Green
    $SourceDocs = getListOfDocs($srcFolder)

    $DestDocs = getListOfDocs($destFolder)

    Write-Host "================================== FILE HASH COMPARE RESULTS ==========================" -ForegroundColor Green

    $result = hashCompare($SourceDocs,$DestDocs)

    Write-Host $result   -ForegroundColor Magenta

}

function hashCompare{
    param(
        [Parameter(Mandatory = $True)]
        $srcDocs,
        $dstDocs
    )

    if($srcDocs -or $dstDocs){
        return (Compare-Object -ReferenceObject $SourceDocs -DifferenceObject $DestDocs  -Property hash -PassThru).Path
    }else {
        return "Source Files and Destination Files hashes shpuld not be empty"
    
    }

}

function getListOfDocs{
    param(
        [Parameter(Mandatory = $True)]
        [string]$pathToDocs
    )
    if($pathToDocs){
        return Get-ChildItem –Path $pathToDocs | foreach  {Get-FileHash –Path $_.FullName}
    }
    else{
        Write-Error 'The source or destination folder not selected, please retry script and select folder' -ErrorAction Stop
    }
    
}

function SelectFolder{
    
       param([string]$Description="Select Folder",[string]$RootFolder="Desktop")

 [System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") |
     Out-Null     

   $objForm = New-Object System.Windows.Forms.FolderBrowserDialog
        $objForm.Rootfolder = $RootFolder
        $objForm.Description = $Description
        $Show = $objForm.ShowDialog()
        If ($Show -eq "OK")
        {
            Return $objForm.SelectedPath
        }
        Else
        {
            Write-Error "Operation cancelled by user."
        }

}


main
