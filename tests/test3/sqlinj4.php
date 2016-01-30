<?php
 $title=$_POST["title"];
 
 $result=mysql_query("SELECT * FROM wp_posts where post_title like '%$title%' and post_status='publish'");
 $found=mysql_num_rows($result);
?>
