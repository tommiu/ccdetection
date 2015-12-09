<?php
// http://www.sitepoint.com/users-php-sessions-mysql/
// --------------------------------------------------

// Check for existing user with the new id

$sql = "SELECT COUNT(*) FROM user WHERE userid = '$_POST[newid]'";
$result = mysql_query($sql);
if (!$result) {
error('A database error occurred in processing your '.
'submission.\nIf this error persists, please '.
'contact you@example.com.');
}
if (@mysql_result($result,0,0)>0) {
error('A user already exists with your chosen userid.\n'.
'Please try another.');
}

?>
