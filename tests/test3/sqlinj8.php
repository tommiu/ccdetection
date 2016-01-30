<?php 
// http://www.sitepoint.com/users-php-sessions-mysql/
// --------------------------------------------------
$sql = "INSERT INTO user SET
userid = '$_POST[newid]',
password = PASSWORD('$newpass'),
fullname = '$_POST[newname]',
email = '$_POST[newemail]',
notes = '$_POST[newnotes]'";
if (!mysql_query($sql))
error('A database error occurred in processing your '.
'submission.\nIf this error persists, please '.
'contact you@example.com.');

?>
