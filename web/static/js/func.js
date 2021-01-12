// web app 中最基本的功能

var inputCount = 0;
let flag = true; // null placeholder

let keywords = [
    '运输航空', '运输周转量', '旅客运输量', '货邮运输量', '旅客吞吐量',
    '东部地区', '东北地区', '中部地区', '西部地区', '货邮吞吐量', '起降架次',
    '大中型飞机', '小型飞机', '经济效益', '主要航空公司', '安康杯',
    '固定资产投资', '一二三三四', '通用航空企业', '消费者投诉', '驾驶员执照', '2017',
    '飞行员数量', '航空货物', '宽体飞机', '窄体飞机', '支线飞机', '服务满意度', '空管系统四类专业技术人员', '严重失信人名单',
    '一加快、两实现'
];
let keynotes = [
    '各项数据为正式年报数据，部分统计数据与此前公布的初步统计数据如有出入，以本次公布数据为准。',
    '涉及的数据为国内航空公司承运的数据。',
    '涉及的数据为国内航空公司承运的数据。',
    '涉及的数据为国内航空公司承运的数据。',
    '指报告期内进港（机场）和出港的旅客人数。',
    '指北京、上海、山东、江苏、天津、浙江、海南、河北、福建和广东10省市。',
    '指黑龙江、辽宁和吉林3省。',
    '指江西、湖北、湖南、河南、安徽和山西6省。',
    '指宁夏、陕西、云南、内蒙古、广西、甘肃、贵州、西藏、新疆、重庆、青海和四川12省（区、市）。',
    '指报告期内货物和邮件的进出港数量。',
    '指报告期内在机场进出港飞机的全部起飞和降落次数，起飞、降落各算一架次。',
    '指座级在100座以上的运输飞机。',
    '指座级在100座以下的运输飞机。',
    '涉及数据为财务快报数据，最终数据以财务年报数据为准。',
    '指南航、国航、东航、海南、深圳、四川、厦门、山东、上海、天津等十家航空公司。',
    '安全生产荣誉奖杯。“安康杯”竞赛活动旨在通过竞赛不断推进企事业单位安全生产工作和安全文化<br>建设，提高全民安全生产意识，从而降低各类事故的发生率和各类职业病的发病率。',
    '未含飞机和特种车辆购租等投资。',
    '指的是“践行一个理念、 推动两翼齐飞、 坚守三条底线、 完善三张网络、 补齐四个短板” 的总体工作思路。',
    '通用航空企业地区分布按民航各地区管理局所辖区域划分。',
    '投诉总数包含旅客与企业自行解决的首次电话投诉。',
    '存在一个飞行员取得多个执照的情况。',
    '2017年度行业综合统计系统正式上线后，由于航空公司生产数据处理流程<br>和审核规则发生变化，2017年度相关数据和增速按照最新的口径进行计算。',
    '飞行员数量来自民航局飞标司',
    '不含邮件、快件',
    '250座级以上的运输飞机',
    '100-200座级运输飞机',
    '100座级以下运输飞机',
    '满分5分，根据中国民航科学技术研究院、中国民航报社、航旅纵横、<br>中国民航机场协会共同发布的《年度中国民航服务旅客满意度评价报告》。',
    '包括空中交通管制员、航空电信人员、航空情报人员和航空气象人员。',
    '依据《关于在一定期限内适当限制特定严重失信人乘坐民用航空器推动社会信用体系建设的意见》<br>（发改财金〔 2018〕 385 号）相关规定。',
    '根据《新时代民航强国建设行动纲要》提出的战略步骤，到2020年，<br>民航加快实现从航空运输大国向航空运输强国的跨越；从2021年到2035年，<br>实现从单一的航空运输强国向多领域的民航强国的跨越；到本世纪中叶，<br>实现由多领域的民航强国向全方位的民航强国的跨越。'
];

$(function () {
    // 输入框：回车键发送
    let inputArea = $('#input-dialog');
    inputArea.keydown(function (e) {
        if(e.keyCode === 13) {
            e.preventDefault();
            send_question();
        }
    })

    // 按钮区：清空按钮
    $('#clear-btn').click(function () {
        inputArea.val("");
    });
    // 发送按钮
    $('#send-btn').click(send_question);

    // 输出框
    let outputArea = document.querySelector('#output-area');
    let nullHeight = outputArea.clientHeight;
    let nullArea = document.querySelector('.null');

    function send_question() {
        // get question string
        let question = inputArea.val();
        if(question === '') {
            alert('问题输入不可为空');
            return ;
        }
        // increase input count
        inputCount++;
        // create question element
        let questionElm = document.createElement('div');
        questionElm.className = 'question';
        questionElm.innerText = '[Q' + inputCount + ']：' + question;
        // clear input area
        outputArea.appendChild(questionElm);
        inputArea.val("");
        // add to output area
        stick_to_bottom();
        // send it to server
        $.ajax({
            url: '/send',
            type: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            data: {
                'question': question,
            },
            success: function (data) {
                // console.log(data);
                setTimeout(function () {
                    add_answer(data);
                }, 500)
            },
            error: function (msg) {
                // console.log(msg);
                show_error(msg);
            }
        });
    }

    function add_answer(data) {
        // create answer element
        let answerElm = document.createElement('div');
        answerElm.className = 'answer';
        // link note to it
        let answer = link_note(data['answer']);
        answerElm.innerHTML = '[A' + inputCount + ']：' + answer;
        // add to output area
        outputArea.appendChild(answerElm);
        init_note();
        // if it has chart
        for(var i = 0; i < data['chart_count']; i++) {
            // create chart canvas
            let chartElm = document.createElement('div');
            chartElm.className = 'answer-chart';
            chartElm.id = 'chart-' + inputCount + '-' + i;
            // add to output area
            outputArea.appendChild(chartElm);
            get_chart(chartElm.id, i);
        }
        stick_to_bottom();
    }

    function get_chart(chart_id, chart_index) {
        var chart = echarts.init(document.getElementById(chart_id), 'white', {renderer: 'canvas'});
        $.ajax({
            type: 'GET',
            url: '/chart',
            dataType: 'json',
            contentType: 'application/json',
            data: {
                'chart_index': chart_index,
            },
            success: function (result) {
                chart.setOption(result);
            },
            error: function (msg) {
                // console.log(msg);
                show_error(msg);
            }
        });
    }

    // 给出关键词语的注释
    function link_note(answer) {
        for(var i=0; i<keywords.length; i++) {
            let j = answer.indexOf(keywords[i]);
            let end = j+keywords[i].length;
            if(j !== -1) {
                return answer.slice(0,j)+'<b data-tooltip="'+keynotes[i]+'">'+answer.slice(j,end)+'</b>'+answer.slice(end,answer.length);
            }
        }
        return answer;
    }

    function init_note() {
        $('[data-tooltip]').addClass('tooltip');
        $('.tooltip').each(function () {
            $(this).append('<span class="tooltip-content">' + $(this).attr('data-tooltip') + '</span>');
        })
        $('.tooltip').mouseover(function () {
            $(this).children('.tooltip-content').css('visibility', 'visible');
        }).mouseout(function () {
            $(this).children('.tooltip-content').css('visibility', 'hidden');
        });
    }

    // 错误
    function show_error(msg) {
        let errElm = document.createElement('div');
        errElm.className = 'answer-error';
        errElm.innerText = msg.toString();
        outputArea.appendChild(errElm);
        stick_to_bottom();
    }

    // 保持发出的问题框在最底下
    function stick_to_bottom() {
        // always stick to bottom
        let n = outputArea.scrollHeight - outputArea.clientHeight;
        outputArea.scrollTop = n;
        if(flag) {
            nullHeight -= n;
            nullArea.style.height = nullHeight + 'px';
            if(nullHeight < 0) {
                nullArea.style.height = '0';
                flag = false;
            }
        }
    }

});
