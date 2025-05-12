from ctypes.wintypes import PWORD

from flask import Flask, request, jsonify, render_template, redirect, url_for, Response, session
import os
import mysql.connector
from urllib.parse import urlparse
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
db_URL = os.environ.get('MYSQL_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='0227',
        database='ff'
    )

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/addvocab', methods=['POST'])
def addvocab():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            word = request.json['word']
            cursor.execute("INSERT INTO vocab (word) VALUES (%s)",
                           (word,))
            conn.commit()
        except Exception as e:
            print("Database error:", e)
            return Response(status=500)
        finally:
            cursor.close()
            conn.close()
        return jsonify({'message': 'Vocab word added'})

@app.route('/removevocab', methods=['POST'])
def removevocab():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            word = request.json['word']
            cursor.execute("DELETE FROM vocab WHERE word =%s", (word,))
            conn.commit()
        except Exception as e:
            print("failed to delete", e)
            return Response(status=500)
        finally:
            cursor.close()
            conn.close()
        return jsonify({'message': 'Vocab deleted'})


@app.route('/sentence_review', methods=['GET'])
def sentence_review():
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT word FROM vocab ORDER BY id DESC LIMIT 8")
            words = cursor.fetchall()
            cursor.close()
            conn.close()
            rs = []
            for (word,) in words:
                try:
                    response = client.responses.create(
                        model='gpt-3.5-turbo',
                        instructions="Take the input word and create a simple sentence that uses the word in its original language.",
                        input=word
                    )
                    sentence = response.output_text.strip()
                    rs.append(sentence)
                except Exception as e:
                    print("error generating content", e)
                    rs.append("error")
            return jsonify(rs)
        except Exception as e:
            print("Database error", e)
            return jsonify({'error': 'error'}), 500



@app.route('/qrespond', methods=['POST', 'GET'])
def qrespond():
    data = request.get_json()
    chatinput = data.get('prompt')
    if not chatinput:
        return jsonify({'error': 'no text provided'}), 400

    try:
        response = client.responses.create(
            model="gpt-3.5-turbo",
            instructions="Respond to the input in the language it was asked in",
            input=chatinput
        )
        output = response.output_text.strip()
        return jsonify({'output': output})
    except Exception as e:
        print(e)
        return jsonify({'error': "AI failure"}), 500




@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'no text provided'}), 400

    try:
        response = client.responses.create(
            model="gpt-3.5-turbo",
            instructions="You are a translation bot, translate the user's input into English.",
            input=text
        )
        translation = response.output_text.strip()
        return jsonify({'translated_text': translation})
    except Exception as e:
        print(e)
        return jsonify({'error': "Translation failure"}), 500


@app.route('/define', methods=['POST'])
def define():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'no text provided'}), 400

    try:
         response = client.responses.create(
         model="gpt-3.5-turbo",
         instructions="You are meant to just provide a definition of the input in the language of the input",
         input=text
         )
         definition = response.output_text.strip()
         return jsonify({'defined_text': definition})
    except Exception as e:
         print(e)
         return jsonify({'error': "Failed to get definition"}), 500


@app.route('/display_vocab', methods=['GET'])
def display_vocab():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT word from vocab ORDER BY id DESC")
        words = cursor.fetchall()
        formatted_words = []
        cursor.close()
        conn.close()
        return jsonify([word[0] for word in words])
    except Exception as e:
        print("Vocab error", e)
        return jsonify({'error': 'Failed'}), 500

@app.route('/story', methods=['GET'])
def story():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT word from vocab ORDER BY id DESC")
        words = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        formatted_words = ', '.join(words)
        response = client.responses.create(
            model="gpt-3.5-turbo",
            instructions= "I will provide you with a list of vocabulary words."
                         "I want you to create a 4 paragraph story in the language of the vocabulary words that utalizes at least 2 vocabulary words per paragraph"
                         "Don't worry about using the word in the exact case and conjugation that it is saved, please use whatever form of the word makes the most sense",
            input=formatted_words
        )
        story = response.output_text.strip()
        return jsonify({'story': story})
    except Exception as e:
        print(e)
        return jsonify({'error': "Intelligence error"}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)