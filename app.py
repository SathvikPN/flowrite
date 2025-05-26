from flask import Flask, jsonify, render_template
import logging
import markdown

app = Flask(__name__)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    with open('content/index_article.md', 'r', encoding='utf-8') as file:
        index_article = file.read()

    article_html = markdown.markdown(index_article)
    return render_template('index.html', data={
        "title": "Home",
        "message": "This is a simple Flask application with logging."
    }, article_html=article_html)

@app.route('/health')
def health():
    logger.info("got ping for health check")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')