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


        case '/getTopicResult':
            $id=$_REQUEST['_id'];
            $result = getTopicResult($id);
            $msg->success = true;
            $msg->data = $result;
            break;
            
        case '/getRelatedDocuments':
            $docs = $_REQUEST['docs'];
            $collection=$_REQUEST['collection'];
            $result = getRelatedDocuments($collection,$docs);
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

function getTopicResult($id){
    $query = array();
    
    $cursor = MongoDao::searchOneById('discuss_result',$id);


    $result = $cursor->topic;
    
    return $result;
}

function getRelatedDocuments($collection,$ids){
    $docids = array();
    $result = array();
    foreach($ids as $id){

        $cursor = MongoDao::searchOneById($collection,$id);
        $temp = new \stdClass();
        $temp->thread_id = $cursor->thread_id;
        $temp-> title = $cursor->title;
        $temp-> timestamp = $cursor->created_time;
        $result[]= $temp;
    }

    return $result;
    

}

