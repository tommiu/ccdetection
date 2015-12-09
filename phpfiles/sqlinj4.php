<?php
 include "db.php";
 
 $title=$_POST["title"];
 
 
 $result=mysql_query("SELECT * FROM wp_posts where post_title like '%$title%' and post_status='publish'");
 $found=mysql_num_rows($result);
 
 if($found>0){
 	while($row=mysql_fetch_array($result)){
 	echo "<li>$row[post_title]</br>
 	        <a href=$row[guid]>$row[guid]</a></li>";
    }   
 }else{
 	echo "<li>No Tutorial Found<li>";
 }
 // ajax search
?>
