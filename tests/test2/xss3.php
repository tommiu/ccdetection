<?php
// http://stackoverflow.com/questions/15251095/display-data-from-sql-database-into-php-html-table
$query = "SELECT * FROM employee"; //You don't need a ; like you do in SQL
$result = mysql_query($query);

echo "<table>"; // start a table tag in the HTML

while($row = mysql_fetch_array($result)){   //Creates a loop to loop through results
echo "<tr><td>" . $row['name'] . "</td><td>" . $row['age'] . "</td></tr>";  //$row['index'] the index here is a field name
}
echo "</table>"; //Close the table in HTML


?>
