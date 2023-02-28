# Define the source and destination paths
$sourcePath = "< SOURCE PATH WHERE CONFIG FILES >"
$destPath = "< DEST PATH WHERE CONFIG FILES LAY >"

# Define the remote server 
$ServerName = "< SERVER IP OR DNS NAME >"
$Port = 5985

# ====================== Step for creating and changing ownership =====================

Write-Host "================ Creating required folders ====================" -ForegroundColor Green
New-Item -ItemType Directory -Path $sourcePath -Force
Write-Host "================= Changing ownership of created folder================="
icacls $sourcePath /grant "NT AUTHORITY\NETWORK SERVICE:(OI)(CI)F"


# ====================== Step checking and configuring WINRM =====================

Write-Host "================= Getting status of WinRM Client ===================================" -ForegroundColor Green
$winrm_status =  Get-Service -Name "*WinRM*" | Select-Object status
$test_winrm_con = Test-WSMan -ComputerName $ServerName -Port $Port
if ($winrm_status.Status -ne "Running" -or -NOT $test_winrm_con ) {

Set-Item -Path WSMan:\localhost\Client\TrustedHosts -Value $ServerName -Concatenate

Test-WSMan -ComputerName $ServerName -Port $Port

# If the test is successful, add the server to the WinRM client
if ($?) {
    Write-Output "============ Adding the server $ServerName to the WinRM client =======" -ForegroundColor Green
    Set-Item -Path WSMan:\localhost\Client\TrustedHosts -Value $ServerName -Concatenate
}
else {
    Write-Error "Unable to connect to the server $ServerName on port $Port" -ForegroundColor DarkRed
    exit
}
}
else {
   Set-Item -Path WSMan:\localhost\Client\TrustedHosts -Value $ServerName -Concatenate
   Write-Host "==================== WinRM client already Running state ======================" -ForegroundColor Green
}

# ====================== Step for installing Newman and it's dependencies =====================
if (Get-Command node.exe -ErrorAction SilentlyContinue) {
    Write-Host "=================== Installing  newman-reporter-teamcity and dependencies =====================" -ForegroundColor Green
    npm install --yes -g newman newman-reporter-teamcity newman-reporter-htmlextra newman-reporter-html
}else {
    Write-Error "-------------------------- Node.js and npm  is not installed -----------------------" -ForegroundColor DarkRed
    exit 1
}


# ================ Copy Newman configuration files to specific folder ===================
$Domain = "< Computer name or AD DNS >"
$Username = "< USERNAME FOR WINRM >"
$Password = "< USER PASSWORD FOR WINRM >"


$DomainUsername = $Domain + "\" + $Username;
$SecurePassword = Convertto-SecureString -String $Password -AsPlainText -force;
$Credentials = New-object System.Management.Automation.PSCredential $DomainUsername, $SecurePassword;

# Create a session to the remote machine using WinRM
$Session = New-PSSession -ComputerName $ServerName  -Credential $Credentials

if ($null -eq $Session) {
    Write-Host "----------------- Failed to connect to the remote server $ServerName -------------------" -ForegroundColor DarkRed
    exit 1
 }
             
 Write-Host "================= Successfull connected to remote server $ServerName ====================" -ForegroundColor Green

 try {
    Write-Host "================ Copying files from $ServerName to Local =================" -ForegroundColor Green
    Copy-Item "$sourcePath\*" -Destination $destPath -FromSession $Session  -Force
    Write-Host "=================== Files Successfully Copied =========================" -ForegroundColor Green
 }
 catch [Exception] {
    Write-Error $_.Exception.Message -ForegroundColor DarkRed
    exit 1;
 }
 


