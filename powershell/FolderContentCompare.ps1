$folders = @{
    "E:\Compare\Example1" = "E:\Compare\Example2";
    }

$OUT_PATH = "."

foreach ($folder in $folders.GetEnumerator()) {
    $key = $folder.Key
    $value = $folder.Value
    $diff = Compare-Object (Get-ChildItem $key -Recurse) (Get-ChildItem $value -Recurse) 
    if ($diff) {
        $folderName = $key.Substring($key.LastIndexOf("\")+1)
        $diff | Select-Object -ExpandProperty InputObject | Out-File -FilePath "$OUT_PATH\$folderName.txt" -Append
    }
}
