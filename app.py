from flask import Flask, jsonify, render_template, request, redirect, session, flash, url_for
import logging
import markdown
from functools import wraps
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

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

def get_db():
    """Connect to the SQLite database, creating it if it doesn't exist, and enable WAL mode."""
    conn = sqlite3.connect(DATABASE, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows

    # TODO: learn more about PRAGMA statements
    conn.execute('PRAGMA journal_mode=WAL;') # Use Write-Ahead Logging for better concurrency
    conn.execute('PRAGMA foreign_keys=ON;')  # Enable foreign key constraints
    logger.info("Connected to the database successfully.")
    return conn

def init_db():
    """Initialize the database using schema.sql."""
    with app.app_context():
        with get_db() as db:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            try:
                with open(schema_path, 'r') as f:
                    db.executescript(f.read())
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                import sys
                sys.exit(1)


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
        # allow only authenticated users to save content
        if 'user_id' not in session:
            logger.warning(f"Unauthenticated user attempted to save content. IP: {request.remote_addr} User-Agent: {request.headers.get('User-Agent')}")
            return render_template('login.html', data={"title": "Login", "message": "login to save content."})

        logger.info(f"Received save from write page. content: \n{request.form.get('content')}")

        user_id = session.get('user_id')
        content = request.form.get('content')
        if content:
            # Insert the post into the database
            with get_db() as db:
                db.execute(
                    "INSERT INTO post (user_id, content, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (user_id, content)
                )
            logger.info(f"User {user_id} saved a new article.")
        return redirect('/shelf')

    return render_template('write.html', data = {
        "title": "Write",
        "message": "Start writing...",
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


@app.route('/shelf')
@login_required
def shelf():
    # Fetch the user's saved articles from the database
    user_id = session.get('user_id')
    with get_db() as db:
        posts = db.execute(
            "SELECT * FROM post WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        ).fetchall()
    
    # Convert posts to a list of dictionaries for rendering
    display_posts = []
    for post in posts:
        display_posts.append({
            "id": post['id'],
            "content": post['content'],
            "created_at": post['created_at']
        })
    logger.info(f"User {user_id} accessed their shelf with {len(display_posts)} articles.")

    return render_template('shelf.html', data = {
        "title": "Shelf",
        "posts": display_posts,
    })

# TODO: check if user is the owner of the post
@app.route('/posts/<int:post_id>')
def view_post(post_id):
    # Get post from database
    with get_db() as db:
        post = db.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
    
    # Check if post exists
    if post is None:
        flash('Post not found', 'error')
        return redirect('/shelf')
    
    return render_template('post.html', post=post)

# TODO: check if user is the owner of the post
@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    # Get post from database
    with get_db() as db:
        post = db.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
    
        # Check if post exists
        if not post:
            flash('Post not found', 'error')
            return redirect('/shelf')
        
        # Check if user owns this post
        if post['user_id'] != session.get('user_id'):
            flash('You do not have permission to edit this post', 'error')
            return redirect('/shelf')
        
        if request.method == 'POST':
            content = request.form.get('content')
            
            if not content:
                flash('Content cannot be empty', 'error')
                return render_template('write.html', post=post)
            
            # Update post in database
            db.execute("UPDATE post SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                      (content, post_id))
            flash('Post updated successfully', 'success')
            return redirect(url_for('view_post', post_id=post_id))
    
    # GET request - show edit form
    return render_template('write.html', data={
        "title": "Edit Post",
        "message": "Edit your post..."
    }, post=post)

# TODO: check if user is the owner of the post
@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    # Delete post from database
    with get_db() as db:
        db.execute("DELETE FROM post WHERE id = ?", (post_id,))
    flash('Post deleted successfully', 'success')
    return redirect('/shelf')





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        # confirm passwords match
        if password != confirmation:
            return render_template(
            'register.html',
            data={"title": "Register", "error": "Mismatched passwords. Please confirm your password."}
            ), 400  # 400 Bad Request for client-side input errors
        
        with get_db() as db:
            # Check if username already exists
            user = db.execute(
                "SELECT * FROM user WHERE username = ?", (username,)
            ).fetchone()
            if user:
                # username already registered, redirect back with message
                return render_template('register.html', data={"title": "Register", "error": "Username is already registered, try a different username."})
            
            # Insert user into user table
            # Hash the password for security
            hashed_password = generate_password_hash(password, method='pbkdf2')
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            logger.info(f"User {username} registered successfully.")
        return redirect('/login')
    return render_template('register.html', data={"title": "Register"})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with get_db() as db:
            user = db.execute(
                "SELECT * FROM user WHERE username = ?", (username,)
            ).fetchone()

            if not user:
                return render_template('login.html', data={
                    "error": "Username not found, please register first.",
                })
            
            # FIX: Use check_password_hash to verify password
            if not check_password_hash(user['password'], password):
                return render_template('login.html', data={
                    "error": "Invalid password. Please try again.",
                })

            # User authenticated successfully
            session['user_id'] = user['id']
            # Optionally update last_login
            db.execute(
                "UPDATE user SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user['id'],)
            )
            logger.info(f"User {username} logged in successfully.")
        # Redirect to the shelf page after successful login
        return redirect('/shelf')

    return render_template('login.html', data={"title": "Login"})

@app.route('/logout')
def logout():
    """Log out the user by clearing the session."""
    logger.info(f"User {session.get('user_id')} is logging out.")
    session.clear()
    logger.info("User logged out successfully.")
    return redirect('/')

if __name__ == '__main__':
    # Path to the SQLite database file
    DATABASE = os.path.join(os.path.dirname(__file__), 'flowrite.db')

    # Always initialize DB to ensure schema exists
    init_db()

    # Start the Flask application
    # app.run(debug=True, port=5001, host='127.0.0.1')
    app.run(debug=True, port=5001, host='0.0.0.0')