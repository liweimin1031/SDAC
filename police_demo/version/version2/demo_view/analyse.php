<?php
require_once dirname(__FILE__) . DIRECTORY_SEPARATOR. 'lib' . DIRECTORY_SEPARATOR.'bootstrap.php';
use Clms\Tools\PhpDao\Mongo\MongoDao;
/* ---------------------------------------------------------------
 Constant definition
 --------------------------------------------------------------- */
$version = 20151126;

if (version_compare(phpversion(), '5.4.0', '<')) {
    if(session_id() == '') {
        session_start();
    }
}
else
{
    if (session_status() == PHP_SESSION_NONE) {
        session_start();
    }
}
$msg = new \stdClass();
$msg->success = false;
$msg->error = new \stdClass();

if(isset($_SESSION) && isset($_SESSION['version']) && $_SESSION['version'] == $version){

}else {
    session_unset();
}


/* ---------------------------------------------------------------
 Function definition
 --------------------------------------------------------------- */
if ( isset($_SERVER['PATH_INFO']) ) {
    switch ($_SERVER['PATH_INFO']) {


        case '/getAnalyse':
            $collection=$_REQUEST['collection'];
            $start=$_REQUEST['start'];
            $end=$_REQUEST['end'];

            getAnalyse($start,$end,$collection);
            break;
            
        default:
            break;
    }
}

echo urldecode ( json_encode($msg));
exit;

function getAnalyse($start,$end,$collection){
    global $msg;

    //exec("python C:\Users\weiminli\workspace\GitHub\SDAC\police_demo\topic\hello.py $start $end $collection",$output, $return_val);
    $cmd="python analyse\script\analyse.py $start $end $collection";

    $shell_data=exec($cmd,$output, $return_val);
    
    //print_r($shell_data);
    if($return_val=='0'){
        $msg->success = true;
    }else{
       $msg->error = 'exec error';        
    }    

    $msg->data =urlencode ( $shell_data);

}


