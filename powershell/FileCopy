param
(
    [string]$sourcePath,
    [string]$destinationPath,
    [string]$fileName
);

<#Выключаем отладочную информацию, чтобы catch ловил ошибку #>
$ErrorActionPreference = "Stop";

try
{
    <#Копирование данных директории #> 
    if ((Test-Path -path $sourcePath) -And (Test-Path -path $destinationPath))
    {
        <#Копируем данные#> 
        Copy-Item -Path $sourcePath\* -Filter "$fileName" -Recurse -Destination $destinationPath -Container
    }

    #Write-Output "Файлы успешно скопированы в папку $destinationPath!";
}
Catch [system.exception]
{
    Write-Output $_.Exception.Message;
    throw [System.ArgumentException] ($_.Exception.Message);
}
