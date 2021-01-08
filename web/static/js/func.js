var inputCount = 0;
let flag = true; // null placeholder

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
                console.log(data);
                setTimeout(function () {
                    add_answer(data);
                }, 500)
            },
            error: function (msg) {
                console.log(msg);
            }
        });
    }

    function add_answer(data) {
        // create answer element
        let answerElm = document.createElement('div');
        answerElm.className = 'answer';
        answerElm.innerText = '[A' + inputCount + ']：' + data['answer'];
        // add to output area
        outputArea.appendChild(answerElm);
        stick_to_bottom();
    }

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
