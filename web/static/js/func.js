// 输入框
let inputArea = document.querySelector('#input-dialog');
var inputCount = 0;

inputArea.addEventListener('keydown', e => {
    if(e.keyCode === 13) {
        e.preventDefault();
        send_question();
    }
});

// 输出框
let outputArea = document.querySelector('#output-area');
let nullArea = document.querySelector('.null');

// 按钮区
let clearBtn = document.querySelector('#clear-btn');
let sendBtn = document.querySelector('#send-btn');

clearBtn.addEventListener('click', clear_question);

let nullHeight = outputArea.clientHeight;
let flag = true; // null placeholder

sendBtn.addEventListener('click', send_question);

// functions
function clear_question() {
    inputArea.value = '';
}

function send_question() {
    // get question string
    let question = inputArea.value;
    if(question === '') {
        alert('问题输入不可为空');
        return ;
    }
    // increase input count
    inputCount++;
    // create question element
    let questionElm = document.createElement('div');
    questionElm.className = 'question';
    questionElm.innerText = '[Q' + inputCount + ']: ' + question;
    outputArea.appendChild(questionElm);
    // clear input area
    clear_question();
    // add to output area
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
