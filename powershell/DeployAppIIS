param(
   [string]$Branch,
   [string]$ArchiveName, 
   [string]$SourceFolder
)
Set-StrictMode -Version Latest
            
$ErrorActionPreference = "Stop";
            
$appPools = @("LIST OF APP POOLS")
            
            
$BranchName = $Branch.Split("/")[0]
$HostIp = "<IP ADDRESS OR DNS OF SERVER >"
$Domain = "< COMPUTER NAME OR AD DNS >"
$Username = "< USER WHO HAS ACCESS TO CONNECTING SERVER >"
$Password = "< USER PASSWORD >"
$DestinationFolder = "< DESTINATION PATH WHERE WEB APP PLACED >"
            
            
$DomainUsername = $Domain + "\" + $Username;
$SecurePassword = Convertto-SecureString -String $Password -AsPlainText -force;
$Credentials = New-object System.Management.Automation.PSCredential $DomainUsername, $SecurePassword;
            
$Session = New-PSSession -ComputerName $HostIp  -Credential $Credentials
            
if ($null -eq $Session) {
   Write-Host "Failed to connect to the remote server $HostIp" -ForegroundColor DarkRed
   exit 1
}
            
Write-Host "Successfull connected to remote server $HostIp" -ForegroundColor DarkGreen
            
[array]$ArchiveExtensions = @("7z", "wim")
            
$mainArchiveName = $ArchiveName + "." + $ArchiveExtensions[0]
try {
   Copy-Item (Join-Path $SourceFolder $mainArchiveName) -Destination $DestinationFolder -ToSession $Session -Force
}
catch [Exception] {
   Write-Error $_.Exception.Message
   exit 1;
}
            
Start-Sleep -s 1
            
Write-Host "Build archive successfully copied to remote server $HostIp" -ForegroundColor DarkGreen
            
$Scriptblock = {
   param(
      $appPools
   )
             
   $ArchiveName = $using:ArchiveName
   $DestinationFolder = $using:DestinationFolder
   $ArchiveExtensions = $using:ArchiveExtensions
   $mainArchiveName = $using:mainArchiveName
             
   # находим путь к программе 7zip
   $7zPath = "C:\Program Files\7-Zip\7z.exe"
   if (-NOT (Test-Path "$7zPath")) {
      $7zPath = "C:\Program Files (x86)\7-Zip\7z.exe"
      if (-NOT (Test-Path "$7zPath")) { throw "7z.exe не найден" }
   }
             
   Function fnStartApplicationPool([string]$appPoolName) {
      import-module WebAdministration
      if ((Get-WebAppPoolState $appPoolName).Value -ne 'Started') {
         Start-WebAppPool -Name $appPoolName
      }
   }
   Function fnStopApplicationPool([string]$appPoolName) {
      import-module WebAdministration
      if ((Get-WebAppPoolState $appPoolName).Value -ne 'Stopped') {
         Stop-WebAppPool -Name $appPoolName
      }
   }
            
             
   foreach ($appPoolName in $appPools) {
      fnStopApplicationPool $appPoolName
      Start-Sleep -s 1
   }
             
   Write-Host "App polls and services successfully stopped"
             
   # Ждем полторы минуты и обновляем метаданные
   Start-Sleep -s 90
             
   if (Test-Path (Join-Path $DestinationFolder $mainArchiveName)) {
      Write-Host "Test: Archive successfully copied" -ForegroundColor DarkGreen
   }
   else {
      throw "Test: Archive failed to copy"
   }
             
   Write-Host "Starting update metadata"
             
   set-alias szip "$7zPath"
             
   # последовательно распаковываем вложенные архивы
   foreach ($archive_extension in $ArchiveExtensions) {
      $archivePath = Join-Path $DestinationFolder ($ArchiveName + "." + $archive_extension)
      szip x "$archivePath" -o"$DestinationFolder" -aoa
      Start-Sleep -s 1
   }
             
   # удаляем архивы после обновления
   foreach ($archive_extension in $ArchiveExtensions) {
      $archivePath = Join-Path $DestinationFolder ($ArchiveName + "." + $archive_extension)
      Remove-Item -Path $archivePath
      Start-Sleep -s 1
   }
             
   Write-Host "Finish update metadata"
             
   # Ждем полторы минуты и запускаем pool-ы и службы
   Start-Sleep -s 90
             
             
   # последовательно запускаем app pool-ы
   foreach ($appPoolName in $appPools) {
      fnStartApplicationPool $appPoolName
      Start-Sleep -s 1
   }
             
   Write-Host "App polls and services successfully started"
             
   return 0;
}
            
try {
   $result = Invoke-Command `
      -Session $Session `
      -ScriptBlock $Scriptblock `
      -ArgumentList $appPools;
}
catch [Exception] {
   Write-Error $_.Exception.Message
   exit 1;
}
               
exit $result
