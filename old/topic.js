var start='2016-07-01';
var end='2016-08-01';
var topic='汇丰'
var oneDay = 24 * 3600 * 1000;
var start_date = Date.parse(start);
var end_date= Date.parse(end);
var dates=(end_date-start_date)/oneDay;
var date=[];
for (var i = 0; i <= dates; i++) {
    var now = new Date(start_date+ i*oneDay);
    var str_date=[now.getFullYear(), now.getMonth()+1 , now.getDate()].join('-');
    date.push(str_date);
}



var start='2016-7-1';
var end='2016-7-7';
var oneDay = 24 * 3600 * 1000;
var start_date = Date.parse(start);
var end_date= Date.parse(end);
var dates=(end_date-start_date)/oneDay;
var date=[];
var data=[];
var posts=[{'title':'t1','last_status':10,'post_create_date':'2016-7-2'},{'title':'t2','last_status':20,'post_create_date':'2016-7-5'},{'title':'t3','last_status':10,'post_create_date':'2016-7-5'}];
for (var i = 0,j=0, posts_len=posts.length; i <= dates; i++) {
    var now = new Date(start_date+ i*oneDay);
    var str_date=[now.getFullYear(), now.getMonth()+1 , now.getDate()].join('-');

    date.push(str_date);
	var titles=[];
	var metion_times=0;
	for ( ;j<posts_len;j++){
		var post=posts[j];
		var post_date=post.post_create_date;
		if (str_date==post_date){
			titles.push(post.title);
			metion_times=metion_times+post.last_status;
			var data_json={
				name:titles,
				value:metion_times
			};
			data.push(data_json);
        }
		else{
          	data.push('-');
			break;
        }
    }
}


option = {
    title: {
        text: 'ECharts 入门示例'
    },
    tooltip: {},
    legend: {
        data:['销量']
    },
    xAxis: {
        data: ["衬衫","羊毛衫","雪纺衫","裤子","高跟鞋","袜子"]
    },
    yAxis: {},
    series: [{
        name: '销量',
        type: 'bar',
        data: [5, 20, 36, 10, 10, 20]
    }]
};