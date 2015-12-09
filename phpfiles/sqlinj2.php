<?php

//end of search form script
if(isset($_GET['by'])){
    $letter=$_GET['by'];
    
    //connect  to the database
    $db=mysql_connect  ("servername", "username",  "password") or die ('I cannot connect to the database  because: ' . mysql_error());
    
    //-select  the database to use
    $mydb=mysql_select_db("yourDatabase");
    
    //-query  the database table
    $sql="SELECT  ID, FirstName, LastName FROM Contacts WHERE FirstName LIKE '%" . $letter . "%' OR LastName LIKE '%" . $letter ."%'";
    
    //-run  the query against the mysql query function
    $result=mysql_query($sql);
    
    //-count  results
    $numrows=mysql_num_rows($result);
    echo  "<p>" .$numrows . " results found for " . $letter . "</p>";
    
    //-create  while loop and loop through result set
    while($row=mysql_fetch_array($result)){
        $FirstName  =$row['FirstName'];
                    $LastName=$row['LastName'];
                    $ID=$row['ID'];
        //-display  the result of the array
        echo  "<ul>\n";
        echo  "<li>" . "<a  href=\"search.php?id=$ID\">"   .$FirstName . " " . $LastName .  "</a></li>\n";
        echo  "</ul>";
    }
}

?>
