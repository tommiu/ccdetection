<?php
// Comments show the abstract version of the PHP code.

// var1 = $_whatever
$user_alcohol_permitted_selection = $_POST['alcohol_check']; //Value sent using jquery .load()

// var2 = list containing string, variable (in this order)
$query="SELECT * FROM social_clubs 
    WHERE name = $user_social_club_name_input" ;

mysql_query($query);
