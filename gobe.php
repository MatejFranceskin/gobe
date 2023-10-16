<?php
$db = new SQLite3('gobe.db');

$where = "";
switch($_GET['type']) {
    case "1":
        $where = "WHERE list80>0";
        break;
    case "2":
        $where = "WHERE list240>0";
        break;
    case "3":
        $where = "WHERE edibility LIKE '%strupena%'";
        break;
}
$query = "SELECT * FROM vrste " . $where . " ORDER BY RANDOM() LIMIT 5";

$result = $db->query($query);

$candidates = array();

while ($row = $result->fetchArray()) {
    $candidates[] = $row;
}

$target = $candidates[0];
$answer = "{$target['name']}, {$target['name_slo']}";
shuffle($candidates);
$options = [];
foreach ($candidates as $candidate) {
    $options[] = "{$candidate['name']}, {$candidate['name_slo']}";
}

$query_slika = "SELECT * FROM slike WHERE vrsta_id = {$target['id']} ORDER BY RANDOM() LIMIT 1";
$result = $db->query($query_slika);
$res = $result->fetchArray();
$obj = (object) [
    'image' => $res['link'],
    'options' => $options,
    'answer' => $answer,
    'link' => $target['link'],
    'protected' => $target['protected'],
    'status' => $target['status'],
    'edibility' => $target['edibility'],
    'comment' => $target['comment']
];

echo json_encode($obj);
?>