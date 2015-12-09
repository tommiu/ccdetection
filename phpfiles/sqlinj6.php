<?php

define ( 'MYSQL_HOST', 'localhost' );
define ( 'MYSQL_BENUTZER', 'root' );
define ( 'MYSQL_KENNWORT', '' );
define ( 'MYSQL_DATENBANK', 'homepageanwendungen' );

$db_link = mysqli_connect (MYSQL_HOST,
                           MYSQL_BENUTZER,
                           MYSQL_KENNWORT,
                           MYSQL_DATENBANK
                          );
if ( ! $db_link )
{
    // hier sollte dann später dem Programmierer eine
    // E-Mail mit dem Problem zukommen gelassen werden
    // die Fehlermeldung für den Programmierer sollte
    // das Problem ausgeben mit: mysql_error()
    die('keine Verbindung zur Zeit möglich - später probieren ');
}

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
if ( ! $db_erg )
{
  die('Ungültige Abfrage: ' . mysql_error());
}

?>
