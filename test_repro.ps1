$body = @{
    message = "Hello"
    channel = "auto"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/message" -Method Post -ContentType "application/json" -Body $body
    Write-Host "Success:"
    $response | ConvertTo-Json
} catch {
    Write-Host "Error:"
    if ($_.Exception.Response) {
        Write-Host "Status Code:" $_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    } else {
        Write-Host $_.Exception.Message
    }
}
