<?php
$sql = " INSERT INTO gaestebuch ";
$sql .= " SET ";
$sql .= " name   ='". $_POST['name'] ."', ";
$sql .= " email  ='". $_POST['email'] ."', ";
$sql .= " url    ='". $_POST['url'] ."', ";
$sql .= " datum  ='". date("Y-m-d H:i:s") ."', ";
$sql .= " eintrag='". $_POST['eintrag'] ."' ";

echo "<hr />SQL: $sql<hr />";

// ausführen des mysql-Befehls
$db_erg = mysqli_query( $db_link, $sql );
?>
