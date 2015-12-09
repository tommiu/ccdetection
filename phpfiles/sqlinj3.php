<?php

//end of our letter search script
if(isset($_GET['id'])){
$contactid=$_GET['id'];
//connect  to the database
$db=mysql_connect  ("servername", "username",  "password") or die ('I cannot connect to the database  because: ' . mysql_error());
//-select  the database to use
$mydb=mysql_select_db("yourDatabase");
//-query  the database table
$sql="SELECT  * FROM Contacts WHERE ID=" . $contactid;
//-run  the query against the mysql query function
$result=mysql_query($sql);
//-create  while loop and loop through result set
while($row=mysql_fetch_array($result)){
  $FirstName =$row['FirstName'];
            $LastName=$row['LastName'];
            $PhoneNumber=$row['PhoneNumber'];
            $Email=$row['Email'];
//-display  the result of the array
echo  "<ul>\n";
echo  "<li>" . $FirstName . " " . $LastName .  "</li>\n";
echo  "<li>" . $PhoneNumber . "</li>\n";
echo  "<li>" . "<a href=mailto:" . $Email .  ">" . $Email . "</a></li>\n";
echo  "</ul>";
}
}

?>
