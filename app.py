from flask import Flask, jsonify, render_template, request, redirect, session
import logging
import markdown
from functools import wraps

app = Flask(__name__)

# TODO: set a secret key for session management(why is this needed?)
app.secret_key = 'your-very-secret-key'  # Needed for session management and security

# TODO: stream log both into console and file
# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    format='%(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    # Debug and Monitoring: Log incoming requests
    # logger.info(f"Received request: {request.method} {request.path} from {request.remote_addr} \ndata: {data}")
    pass

# Endpoint to check if the server is running
@app.route('/health')
def health():
    # TODO: add checks: database connection, external service availability
    logger.info("Health check endpoint called")
    return jsonify({"status": "OK"})

# Endpoint for landing page
@app.route('/')
def index():
    with open('content/index_article.md', 'r', encoding='utf-8') as file:
        index_article = file.read()
    article_html = markdown.markdown(index_article)
    return render_template('index.html', data = {
        "title": "Home",
        "message": "Hompe Page for Flowrite",
    }, article_html=article_html)

# Endpoint to serve WRITE editor page
@app.route('/write', methods=['GET', 'POST'])
def write():
    # user submitted content from the editor to save
    if request.method == 'POST':
        logger.info(f"Received save from write page: content: \n{request.form.get('content')}")
        return redirect('/shelf')
    

    return render_template('write.html', data = {
        "title": "Write",
    })



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


# Middleware to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Unauthenticated: user not logged in (no user_id in session)
        if 'user_id' not in session:
            logger.warning("Unauthenticated access for the requested resource")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


if __name__ == '__main__':
    # app.run(debug=True, port=5001, host='127.0.0.1')
    app.run(debug=True, port=5001, host='0.0.0.0')