function createPic(maxNum,checkNum) {
    var percentInfo = $('#percentInfo').val();
    var obj2=eval("("+percentInfo+")");
    var reallyPercent = obj2[checkNum-1];
    console.log(reallyPercent);
    for(var i=1;i<=maxNum;i++){
        var dom = document.getElementById("container"+i);
        var myChart = echarts.init(dom);
        var app = {};
        option = null;
        option = {
            title : {
                text: reallyPercent[i-1][0],
                subtext: '',
                x:'center'
            },
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                data: ['正确','错误']
            },
            series : [
                {
                    name: '访问来源',
                    type: 'pie',
                    radius : '55%',
                    center: ['50%', '60%'],
                    data:[
                        {value:reallyPercent[i-1][1][1]-reallyPercent[i-1][1][0], name:'正确'},
                        {value:reallyPercent[i-1][1][0], name:'错误'},
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };
        if (option && typeof option === "object") {
            myChart.setOption(option, true);
        }
    }
}
