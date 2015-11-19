<?php
mysql_query($query);
$user_alcohol_permitted_selection = $_POST['alcohol_check']; //Value sent using jquery .load()

$query="SELECT * FROM social_clubs 
        WHERE name = $user_social_club_name_input" ;

$query.= "AND WHERE alcohol_permitted = $user_alcohol_permitted_selection";

// mysql_query($_POST["test"]);
?>

<?php
    echo "test";
?>

<?php
    // test
    echo "test2";
?>
