Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice("Microsoft Zira Desktop")
$synth.Rate = 0
$outDir = "C:\Users\Samuel\Downloads\legible\demo\video\raw"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
Get-Content "C:\Users\Samuel\Downloads\legible\demo\video\work\vo_script.txt" | ForEach-Object {
    $parts = $_ -split '\|', 2
    $n = $parts[0]
    $text = $parts[1]
    $path = Join-Path $outDir "vo_$n.wav"
    $synth.SetOutputToWaveFile($path)
    $synth.Speak($text)
    $synth.SetOutputToNull()
    Write-Host "wrote $path"
}
