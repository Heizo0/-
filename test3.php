<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Prompt 發送工具</title>
</head>
<body>
<h2>Prompt 測試工具</h2>

<form method="post">
    <label>頻率（秒）:</label><br>
    <input type="number" step="0.1" name="interval" required><br><br>

    <label>次數:</label><br>
    <input type="number" name="count" required><br><br>

    <button type="submit">發送 Prompt</button>
</form>
<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $interval = escapeshellarg($_POST["interval"]);
    $count = escapeshellarg($_POST["count"]);
    $python = "python";
    $script = "send_prompt.py";
    $command = "$python $script $interval $count";
    echo "<pre>";
    echo shell_exec($command);
    echo "</pre>";
}
?>
</body>
</html>
