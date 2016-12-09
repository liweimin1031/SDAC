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
            $id=$_REQUEST['_id'];
            $result = getLinkageResult($id);
            $msg->success = true;
            $msg->data = $result;
            break;
            
        case '/getUserProfile':
            $username = $_REQUEST['username'];
            $result = getUserProfile($username);
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

function getLinkageResult($id){

    $cursor = MongoDao::searchOneById('discuss_result',$id);
    $result = $cursor->linkage;
    
    return $result;
}

function getUserProfile($username){
    $query = array('name'=>$username);
    $cursor = MongoDao::searchOne('discuss_user',$query);
    $result = new \stdClass();
    $result->userid = $cursor->userid;
    $result->name = $cursor->name;
    $result-> register_time = $cursor->register_time;
    $result-> img = $cursor->img;

    return $result;
    

}

