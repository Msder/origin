var dom = document.getElementById("container1");
var myChart = echarts.init(dom);
var app = {};
option = null;
var qtype = $('#type').html().split('-');
var data = genData();

console.log(qtype);
option = {
    title : {
        text: '题目类型图饼',
        subtext: '',
        x:'center'
    },
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        type: 'scroll',
        orient: 'vertical',
        right: 10,
        top: 20,
        bottom: 20,
        data: data.legendData,

        selected: data.selected
    },
    series : [
        {
            name: '类型',
            type: 'pie',
            radius : '55%',
            center: ['40%', '50%'],
            data: data.seriesData,
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




function genData() {
    var nameList = [
        '机器人形象','机器人定义','机器人分类','机器人结构','稳定性','斜面','摩擦力','力','功','单摆','杠杆','轮轴','滑轮组','传动链','风扇'
    ];
    var legendData = [];
    var seriesData = [];
    var selected = {};
    for (var i = 0; i < nameList.length; i++) {
        legendData.push(nameList[i]);
        seriesData.push({
            name: nameList[i],
            value: qtype[i],
        });
        console.log("种类数量："+qtype[i]);
        selected[nameList[i]] = qtype[i]>0;
        if(qtype[i]>0){
            $('#TypeDowebok').append('<li><input type="checkbox" name="type" class="'+qtype[i]+'" data-labelauty="'+nameList[i]+'(共'+qtype[i]+'题)'+'" value="'+(parseInt(i)+1)+'"></li>');
        }
    }
    for(var i =0; i <15;i++){
        console.log("是否选择:"+selected[nameList[i]]);
    }
    return {
        legendData: legendData,
        seriesData: seriesData,
        selected: selected
    };

    function makeWord(max, min) {
        var nameLen = Math.ceil(Math.random() * max + min);
        var name = [];
        for (var i = 0; i < nameLen; i++) {
            name.push(nameList[Math.round(Math.random() * nameList.length - 1)]);
        }
        return name.join('');
    }
}
if (option && typeof option === "object") {
    myChart.setOption(option, true);
}