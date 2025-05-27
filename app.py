from flask import Flask, jsonify, render_template, request, redirect
import logging
import markdown
from functools import wraps

app = Flask(__name__)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    format='%(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    pass
    # if request.method == 'POST':
    #     data = request.form.to_dict()
    # elif request.method == 'GET':
    #     data = request.args.to_dict()
    # logger.info(f"Received request: {request.method} {request.path} from {request.remote_addr} \ndata: {data}")

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
        # print(f"Received save from write page: content: \n{request.form.get('content')}")
        redirect('/shelf')
    

    return render_template('write.html', data = {
        "title": "Write",
    })

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

@app.route('/shelf')
# @login_required
def shelf():
    # Here you would typically fetch the user's saved articles from a database
    # For demonstration, we'll use a static list
    articles = [
        {"title": "Article 1", "content": "Content of article 1"},
        {"title": "Article 2", "content": "Content of article 2"},
        {"title": "Article 3", "content": "Content of article 3"},
    ]
    
    return render_template('shelf.html', data = {
        "title": "Shelf",
        "articles": articles,
    })


if __name__ == '__main__':
    # app.run(debug=True, port=5001, host='127.0.0.1')
    app.run(debug=True, port=5001, host='0.0.0.0')