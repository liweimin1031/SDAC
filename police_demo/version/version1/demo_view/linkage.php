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


        case '/getLinkageResult':

            $result = getLinkageResult();
            $msg->success = true;
            $msg->data = $result;
            break;
            
        case '/getUserProflie':
            $docs = $_REQUEST['docs'];
            $result = getUserProflie($docs);
            $msg->success = true;
            $msg->data = $result;
            break;
        default:
            break;
    }
}

if($msg->success ==false && get_object_vars($msg->error) == false){
    $msg->error->reason = 'Unknown server error';
}
echo json_encode($msg);
exit;

function getLinkageResult(){
    $query = array();

    $cursor = MongoDao::search('discuss_result',$query);
    //exec("python C:\Users\weiminli\workspace\GitHub\SDAC\police_demo\topic\test.py $data_source $time_range");
    $result = array();
    foreach ($cursor as $doc) {
        $result = $doc->topic;
    }
    return $result;
}

function getUserProflie($name){
    $query = array('name'=$name);
    $cursor = MongoDao::search('discuss_user',$query);
    $result = new \stdClass();
    $result->userid = $cursor->userid;
    $result->name = $cursor->name;
    $result-> register_time = $cursor->register_time;
    $result-> img = $cursor->img;

    return $result;
    

}

