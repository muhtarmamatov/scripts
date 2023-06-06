$Path="FULL_PATH_TO_FILES"

Get-ChildItem -Path $Path -Recurse -Filter "Web.config" | ForEach-Object {
$newName = $_.FullName + ".orig"
Rename-Item $_.FullName $newName
}