from flask import render_template, request, jsonify

from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/send', methods=['GET', 'POST'])
def send():
    question = request.values.get('question')
    return jsonify({'answer': question})
