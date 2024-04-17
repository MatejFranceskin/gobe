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
        $where = "WHERE name LIKE '%boletus%' OR name LIKE '%leccin%' OR name LIKE '%suill%' OR name LIKE '%imperator%' OR name LIKE '%tylopilus%' OR name LIKE '%baorangia%' OR name LIKE '%lanmaoa%' OR name LIKE '%imleria%' OR name LIKE '%xerocom%' OR name LIKE '%chalciporus%' OR name LIKE '%gyroporus%' OR name LIKE '%porphyrellus%' OR name LIKE '%gyrodon%' OR name LIKE '%phylloporus%' OR name LIKE '%strobilomyces%'";
        break;
    case "4":
       $where = "WHERE edibility LIKE '%strupena%'";
        break;
    case "5":
        $where = "WHERE protected>0";
        break;
    case "6":
        $where = "WHERE status!=''";
        break;
}

$objects = array();
$query = "SELECT * FROM vrste " . $where . " ORDER BY RANDOM()";
$result = $db->query($query);

while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
#    $query_slika = "SELECT * FROM slike WHERE vrsta_id = {$row['id']} ORDER BY RANDOM()";
    $query_slika = "SELECT * FROM slike WHERE vrsta_id = {$row['id']} AND author = quiz ORDER BY link";
    $result2 = $db->query($query_slika);
    $slike = array();
    while ($res = $result2->fetchArray(SQLITE3_ASSOC)) {
        $slike[] = $res['link'];
    }
	$full_name = $row['full_name'];
	$a =  explode(' ', $full_name);
    $name = "{$a[0]} {$a[1]}, {$row['name_slo']}";
    $objects[] = (object) [
        'images' => $slike,
        'name' => $name,
        'link' => $row['link'],
        'protected' => $row['protected'],
        'status' => $row['status'],
        'edibility' => $row['edibility'],
        'comment' => $row['comment']
    ];
}

echo json_encode($objects);
?>