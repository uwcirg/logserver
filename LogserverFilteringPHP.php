<?php
// Database configuration
define('DB_HOST', 'postgres://app_user:secret@postgres:5432/app_db');
define('DB_NAME', 'app_db');
define('DB_USER', 'app_user');
define('DB_PASS', 'secret');

try {
    // Create PDO connection
    $pdo = new PDO("pgsql:host=".DB_HOST.";dbname=".DB_NAME, DB_USER, DB_PASS);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Initialize base query
    $query = "SELECT id, event FROM events WHERE 1=1";
    $params = [];

    // Build filters from GET parameters
    $filters = [
        'user_id' => "event->'agent'->>'who' = :user_id",
        'ip_address' => "event->'agent'->>'ip_address' = :ip_address",
        'user_agent' => "event->'agent'->>'user_agent' = :user_agent",
        'action' => "event->>'action' = :action",
        'controller' => "event->'entity'->'detail'->>'controller' = :controller",
        'log_level' => "event->>'level' = :log_level",
        'source_observer' => "event->'source'->>'observer' = :source_observer",
        'start_date' => "event->>'occurred' >= :start_date",
        'end_date' => "event->>'occurred' <= :end_date"
    ];

    foreach ($filters as $key => $clause) {
        if (!empty($_GET[$key])) {
            $query .= " AND " . $clause;
            $params[":$key"] = $_GET[$key];
        }
    }

    // Add sorting and limiting
    $query .= " ORDER BY (event->>'occurred') DESC LIMIT 2500";

    // Prepare and execute query
    $stmt = $pdo->prepare($query);
    $stmt->execute($params);
    $logs = $stmt->fetchAll(PDO::FETCH_ASSOC);

} catch(PDOException $e) {
    die("ERROR: Could not connect. " . $e->getMessage());
}
?>

// VIEWS needs to be integrated with current website


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Log Viewer</title>
    <style>
        .filter-form { margin: 20px; padding: 20px; background: #f5f5f5; }
        .filter-group { margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #f2f2f2; }
        pre { white-space: pre-wrap; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Log Viewer</h1>
    
    <!-- Filter Form -->
    <form class="filter-form" method="get">
        <div class="filter-group">
            <label>User ID: <input type="text" name="user_id" value="<?= htmlspecialchars($_GET['user_id'] ?? '') ?>"></label>
            <label>IP Address: <input type="text" name="ip_address" value="<?= htmlspecialchars($_GET['ip_address'] ?? '') ?>"></label>
            <label>Start Date: <input type="datetime-local" name="start_date" value="<?= htmlspecialchars($_GET['start_date'] ?? '') ?>"></label>
            <label>End Date: <input type="datetime-local" name="end_date" value="<?= htmlspecialchars($_GET['end_date'] ?? '') ?>"></label>
        </div>
        <div class="filter-group">
            <label>Controller: 
                <select name="controller">
                    <option value="">All</option>
                    <option value="users" <?= ($_GET['controller'] ?? '') == 'users' ? 'selected' : '' ?>>Users</option>
                </select>
            </label>
            <label>Action: 
                <select name="action">
                    <option value="">All</option>
                    <option value="read" <?= ($_GET['action'] ?? '') == 'read' ? 'selected' : '' ?>>Read</option>
                </select>
            </label>
            <label>Log Level: 
                <select name="log_level">
                    <option value="">All</option>
                    <option value="info" <?= ($_GET['log_level'] ?? '') == 'info' ? 'selected' : '' ?>>Info</option>
                    <option value="error" <?= ($_GET['log_level'] ?? '') == 'error' ? 'selected' : '' ?>>Error</option>
                </select>
            </label>
        </div>
        <button type="submit">Filter Logs</button>
    </form>

    <!-- Results -->
    <h2>Results (<?= count($logs) ?>)</h2>
    <?php if (!empty($logs)): ?>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>User ID</th>
                    <th>IP Address</th>
                    <th>Action</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($logs as $log): 
                    $event = json_decode($log['event'], true);
                ?>
                    <tr>
                        <td><?= htmlspecialchars($event['occurred'] ?? '') ?></td>
                        <td><?= htmlspecialchars($event['agent']['who'] ?? '') ?></td>
                        <td><?= htmlspecialchars($event['agent']['ip_address'] ?? '') ?></td>
                        <td><?= htmlspecialchars($event['action'] ?? '') ?></td>
                        <td>
                            <pre><?= htmlspecialchars(json_encode($event, JSON_PRETTY_PRINT)) ?></pre>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    <?php else: ?>
        <p>No logs found matching the filters.</p>
    <?php endif; ?>
</body>
</html>