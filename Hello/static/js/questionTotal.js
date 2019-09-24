var dom = document.getElementById("container");
var myChart = echarts.init(dom);
var app = {};
var mainType = $('#mainType').html().split('-');
var singleSum = mainType[0];
var multipleSum = mainType[1];
var judgeSum = mainType[2];
option = null;
option = {
    backgroundColor: '#2c343c',

    title: {
        text: '题目饼图',
        left: 'center',
        top: 20,
        textStyle: {
            color: '#ccc'
        }
    },

    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },

    visualMap: {
        show: false,
        min: 80,
        max: 600,
        inRange: {
            colorLightness: [0, 1]
        }
    },
    series : [
        {
            name:'数量和比例',
            type:'pie',
            radius : '55%',
            center: ['50%', '50%'],
            data:[
                {value:singleSum, name:'单选题'},
                {value:multipleSum, name:'多选题'},
                {value:judgeSum, name:'判断题'},
            ].sort(function (a, b) { return a.value - b.value; }),
            roseType: 'radius',
            label: {
                normal: {
                    textStyle: {
                        color: 'rgba(255, 255, 255, 0.3)'
                    }
                }
            },
            labelLine: {
                normal: {
                    lineStyle: {
                        color: 'rgba(255, 255, 255, 0.3)'
                    },
                    smooth: 0.2,
                    length: 10,
                    length2: 20
                }
            },
            itemStyle: {
                normal: {
                    color: '#c23531',
                    shadowBlur: 200,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            },

            animationType: 'scale',
            animationEasing: 'elasticOut',
            animationDelay: function (idx) {
                return Math.random() * 200;
            }
        }
    ]
};
if (option && typeof option === "object") {
    myChart.setOption(option, true);
}
