<?php 
	require "rb-mysql.php";
	R::setup('mysql:host=localhost;
        dbname=alexa5x9_users','alexa5x9_users','');
	if ( !R::testConnection() )
	{
        exit ('Проверьте подключение к интернету. Если у Вас всё работает, то приносим извинения за технические неполадки.');
	}

	$base1 = R::findAll('table2');
	$base2 = R::findAll('table4');
	$result = array('base1'=> json_encode($base1),'base2'=>json_encode($base2) ); 


	header('Content-type: application/json');
	echo json_encode($result);
?>


