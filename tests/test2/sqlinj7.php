<?php
// http://www.sitepoint.com/users-php-sessions-mysql/
// --------------------------------------------------

// Check for existing user with the new id

$sql = "SELECT COUNT(*) FROM user WHERE userid = '$_POST[newid]'";
$result = mysql_query($sql);
?>
