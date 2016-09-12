//yunzhao Demo of Rasch Model
/*DEMO:
https://elana.org/demo/index.html#basic
HKEAA DATA:
https://elana.org/hkeaa/report.php
*/
optionobj.onclick = function(params) {
      var html = “”;
      html += '<div style="z-index:1000;margin:200px 0px 0px 300px;position:relative;overflow-y:auto;max-height:500px;background:#fff;height:100%;width:400px;">';
      html += params[0]….
      html += '</div>'; 
      var popLink = document.createElement('div');
      popLink.innerHTML = html;
      var downloadDiv = document.createElement('div');
      downloadDiv.id = echartsClickId;
      downloadDiv.style.cssText = 'position:fixed;'
                + 'z-index:999;'
                + 'display:block;'
                + 'top:0;left:0;'
                + 'background-color:rgba(33,33,33,0.5);'
                + 'text-align:center;'
               + 'width:100%;'
                + 'height:100%;';
                //+ 'line-height:'
                //+ document.documentElement.clientHeight + 'px;';

      downloadDiv.appendChild(popLink);
      document.body.appendChild(downloadDiv);
      popLink = null;
      downloadDiv = null;
      setTimeout(function (){
          var _d = document.getElementById(echartsClickId);
          if (_d) {
              _d.onclick = function () {
                  var d = document.getElementById(
                      echartsClickId
                  );
                  d.onclick = null;
                  d.innerHTML = '';
                  document.body.removeChild(d);
                  d = null;
              };
              _d = null;
          }
      }, 500);
}

            myChart = echarts.init(domMain, curTheme);
            window.onresize = myChart.resize;
            if(optionobj && optionobj.onclick) {
                var ecConfig = require('echarts/config');
                myChart.on(ecConfig.EVENT.CLICK, optionobj.onclick);
            }
            myChart.setOption(optionobj.optiondata, true);
