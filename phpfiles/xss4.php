<?php
// http://www.php-kurs.com/mysql-datenbank-auslesen.htm
// ----------------------------------------------------

$db_erg = mysqli_query( $db_link, $sql );
if ( ! $db_erg )
{
  die('Ungültige Abfrage: ' . mysqli_error());
}
 
echo '<table border="1">';
while ($zeile = mysqli_fetch_array( $db_erg, MYSQL_ASSOC))
{
  echo "<tr>";
  echo "<td>". $zeile['id'] . "</td>";
  echo "<td>". $zeile['nachname'] . "</td>";
  echo "<td>". $zeile['vorname'] . "</td>";
  echo "<td>". $zeile['akuerzel'] . "</td>";
  echo "<td>". $zeile['strasse'] . "</td>";
  echo "<td>". $zeile['plz'] . "</td>";
  echo "<td>". $zeile['telefon'] . "</td>";
  echo "</tr>";
}
echo "</table>";
 
mysqli_free_result( $db_erg );
?>
