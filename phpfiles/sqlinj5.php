<?php
$eintrag = "INSERT INTO Tabellenname
(url, urlname, name, beschreibung)
VALUES
('$url', '$urlname', '$name', '$beschreibung')";

$eintragen = mysql_query($eintrag);
?>

<?php
if($eintragen == true)
   {
   echo "Eintrag war erfolgreich";
   }
else
   {
   echo "Fehler beim Speichern";
   }
?>
