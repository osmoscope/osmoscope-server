from flask import Flask

app = Flask(__name__)
 
@app.route('/')
def osmoscope_server():
    return 'This is osmoscope server'
 
if __name__ == '__main__':
    app.run(host='0.0.0.0')
