<?php
$eintrag = "INSERT INTO Tabellenname
(url, urlname, name, beschreibung)
VALUES
('$url', '$urlname', '$name', '$beschreibung')";

$eintragen = mysql_query($eintrag);
?>
