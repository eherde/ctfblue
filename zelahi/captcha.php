session_start();

$possible = '126bdhcpqwjsanzmz';
$characters = 5;
$str="";
$i = 0;

while ($i < $characters) {
	$str .= substr($possible, mt_rand(0,strlen($possible)-1), 1);
	$i++;
}
$_SESSION['captchacode']=$str;