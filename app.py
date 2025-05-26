from flask import Flask, jsonify, render_template
import logging

app = Flask(__name__)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    logger.info("Home route accessed")
    return render_template('index.html')

@app.route('/health')
def health():
    logger.info("got ping for health check")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')