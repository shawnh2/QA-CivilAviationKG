from flask import render_template, request, jsonify

from . import main
from chatbot import CAChatBot

chatbot = CAChatBot(mode='web')
temp_charts = []


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/send', methods=['GET', 'POST'])
def send_answer():
    global temp_charts

    question = request.values.get('question')
    answers = chatbot.query(question)
    charts = []
    if len(answers) == 2:
        answers, charts = answers
    temp_charts = charts
    return jsonify({'answer': answers, 'chart_count': len(charts)})


@main.route('/chart', methods=['GET', 'POST'])
def send_chart():
    global temp_charts

    i = int(request.values.get('chart_index'))
    return temp_charts[i].dump_options()
