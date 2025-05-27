from flask import Flask, jsonify, render_template, request
import logging
import markdown

app = Flask(__name__)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/health')
def health():
    logger.info("got ping for health check")
    return jsonify({"status": "ok"})


@app.route('/')
def index():
    with open('content/index_article.md', 'r', encoding='utf-8') as file:
        index_article = file.read()
    article_html = markdown.markdown(index_article)
    return render_template('index.html', data = {
        "title": "Home",
        "message": "Hompe Page for Flowrite",
    }, article_html=article_html)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        # Handle form submission logic here
        print(f"Received save from write page: content: \n{request.form.get('content')}")
        return jsonify({"status": "success", "message": "Content saved successfully!"})
    

    return render_template('write.html', data = {
        "title": "Write",
        "message": "Write Page for Flowrite",
    }, user = {
        "is_authenticated": False,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')