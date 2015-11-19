<?php

echo "test";

$abc = "whatever";

$user_alcohol_permitted_selection = $_POST['alcohol_check'] + "abc" + $_POST["test"]; //Value sent using jquery .load()

$query="SELECT * FROM social_clubs 
        WHERE name = $user_social_club_name_input" ;

$query.= "AND WHERE alcohol_permitted = $user_alcohol_permitted_selection";


echo "test2";

$def = "whatever2";

mysql_query($query);

mysql_query($_POST["test"]);
?>
