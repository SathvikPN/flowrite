from flask import Flask, jsonify, render_template, request, redirect, session, flash, url_for
import logging
import markdown
from functools import wraps
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import uuid
import logging.handlers
import secrets

app = Flask(__name__)

# Security Configurations (cursor assisted rewrite)
app.secret_key = secrets.token_hex(32)  # Generate a secure random key
app.config.update(
    SESSION_COOKIE_SECURE=True,          # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,        # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE='Lax',      # CSRF protection
    PERMANENT_SESSION_LIFETIME=1800,     # Session timeout (30 minutes)
    MAX_CONTENT_LENGTH=10 * 1024 * 1024 # Max content length (10MB)
)

# Rate Limiter Configuration (cursor assisted rewrite) read: https://flask-limiter.readthedocs.io/en/stable/
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use memory for development, redis:// for production
)

# Security Context for Logging
class SecurityLoggingFilter(logging.Filter):
    def filter(self, record):
        try:
            from flask import has_request_context, request
            if has_request_context():
                record.remote_addr = request.remote_addr
                record.user_id = session.get('user_id', 'No User')
                record.url = request.url
            else:
                record.remote_addr = 'No Request Context'
                record.user_id = 'No Request Context'
                record.url = 'No Request Context'
        except Exception:
            record.remote_addr = 'Error'
            record.user_id = 'Error'
            record.url = 'Error'
        return True

# Enhanced Logging Configuration
def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Main application logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # File Handler for general logs
    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        when='midnight',
        interval=1,
        backupCount=30
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(remote_addr)s] - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Security Event Handler
    security_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        when='midnight',
        interval=1,
        backupCount=90
    )
    security_handler.setLevel(logging.WARNING)
    security_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(remote_addr)s] - User:%(user_id)s - %(message)s'
    )
    security_handler.setFormatter(security_format)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(security_handler)
    
    # Add the security filter
    logger.addFilter(SecurityLoggingFilter())
    
    return logger

# Initialize logger
logger = setup_logging()

@app.before_request
def before_request():
    # Generate request ID for tracking
    request.id = str(uuid.uuid4())
    # Add timestamp for request duration tracking
    request._start_time = datetime.utcnow()
    
    # Log incoming requests with context
    logger.info(
        f"Request {request.id}: {request.method} {request.path}",
        extra={
            'request_id': request.id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else 'No User Agent'
        }
    )

@app.after_request
def after_request(response):
    # Calculate request duration
    duration = datetime.utcnow() - request._start_time
    
    # Log response details
    logger.info(
        f"Request {request.id} completed in {duration.total_seconds():.3f}s with status {response.status_code}",
        extra={
            'request_id': request.id,
            'duration': duration.total_seconds(),
            'status_code': response.status_code
        }
    )
    
    # Add security headers (cursor assisted)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

def get_db():
    """Connect to the SQLite database, creating it if it doesn't exist, and enable WAL mode."""
    conn = sqlite3.connect(DATABASE, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_db():
    """Initialize the database using schema.sql."""
    with app.app_context():
        with get_db() as db:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            try:
                with open(schema_path, 'r') as f:
                    db.executescript(f.read())
                logger.info("Database schema initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                import sys
                sys.exit(1)
            
            try:
                # Enable WAL mode and foreign keys
                db.execute('PRAGMA journal_mode=WAL;')
                db.execute('PRAGMA foreign_keys=ON;')
                logger.info("Database configuration completed successfully")
            except Exception as e:
                logger.error(f"Failed to configure database: {e}")
                sys.exit(1)

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
@limiter.limit("30 per hour")  # Prevent spam (cursor assisted)
def write():
    if request.method == 'POST':
        content = request.form.get('content')
        user_id = session.get('user_id')

        if not content:
            logger.warning(f"Empty content submission attempt by user {user_id}")
            flash('Content cannot be empty', 'error')
            return redirect('/write')

        if len(content) > 50000:  # Example content length limit
            logger.warning(f"Oversized content submission attempt by user {user_id}")
            flash('Content exceeds maximum length', 'error')
            return redirect('/write')

        with get_db() as db:
            try:
                db.execute(
                    "INSERT INTO post (user_id, content, created_at, ip_address) VALUES (?, ?, CURRENT_TIMESTAMP, ?)",
                    (user_id, content, request.remote_addr)
                )
                logger.info(f"New post created by user {user_id}")
                
            except sqlite3.Error as e:
                logger.error(f"Database error while saving post: {e}")
                flash('Failed to save post. Please try again.', 'error')
                return redirect('/write')

        return redirect('/shelf')

    return render_template('write.html', data={"title": "Write"})

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
@limiter.limit("10 per minute")  # Prevent rapid deletion (cursor assisted)
def delete_post(post_id):
    user_id = session.get('user_id')
    
    with get_db() as db:
        try:
            # First check if post exists and belongs to user
            post = db.execute(
                "SELECT user_id FROM post WHERE id = ?", 
                (post_id,)
            ).fetchone()
            
            if not post:
                logger.warning(f"Delete attempt on non-existent post {post_id} by user {user_id}")
                flash('Post not found', 'error')
                return redirect('/shelf')
            
            if post['user_id'] != user_id:
                logger.warning(
                    f"Unauthorized delete attempt on post {post_id} by user {user_id}",
                    extra={'severity': 'high', 'attempt_type': 'unauthorized_deletion'}
                )
                flash('Unauthorized action', 'error')
                return redirect('/shelf'), 403
            
            # If checks pass, delete the post
            db.execute("DELETE FROM post WHERE id = ?", (post_id,))
            logger.info(f"Post {post_id} deleted by user {user_id}")
            flash('Post deleted successfully', 'success')
            
        except sqlite3.Error as e:
            logger.error(f"Database error while deleting post {post_id}: {e}")
            flash('Failed to delete post. Please try again.', 'error')
    
    return redirect('/shelf')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")  # Strict limit on registration attempts
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Enhanced input validation
        if not username or not password or not confirmation:
            logger.warning(f"Registration attempt with missing fields from {request.remote_addr}")
            return render_template('register.html', data={"error": "All fields are required"}), 400

        if password != confirmation:
            logger.warning(f"Registration attempt with mismatched passwords from {request.remote_addr}")
            return render_template('register.html', data={"error": "Mismatched Passwords. Please reconfirm"}), 400
        
        with get_db() as db:
            try:
                # Check if username already exists
                user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
                if user:
                    logger.warning(f"Registration attempt with existing username '{username}' from {request.remote_addr}")
                    return render_template('register.html', data={"error": "Username already exists"}), 400
                
                # Hash the password with strong parameters
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256:260000')
                
                # Insert user with creation timestamp
                db.execute(
                    "INSERT INTO user (username, password, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (username, hashed_password)
                )
                logger.info(f"New user registered: {username} from {request.remote_addr}")
                
            except sqlite3.Error as e:
                logger.error(f"Database error during registration: {e}")
                return render_template('register.html', data={"error": "Registration failed. Please try again."}), 500

        return redirect('/login')
    return render_template('register.html', data={"title": "Register"})

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Prevent brute force attempts
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Enhanced input validation
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
            return render_template('login.html', data={"error": "Both username and password are required"}), 400

        with get_db() as db:
            try:
                user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

                if not user or not check_password_hash(user['password'], password):
                    logger.warning(
                        f"Failed login attempt for user '{username}' from {request.remote_addr}",
                        extra={'attempt_type': 'invalid_credentials'}
                    )
                    # Use a generic error message to prevent user enumeration
                    return render_template('login.html', data={"error": "Invalid username or password"}), 401

                # Successful login
                session.clear()  # Clear any existing session
                session['user_id'] = user['id']
                session['username'] = user['username']
                session.permanent = True  # Use permanent session with lifetime set in config
                
                # Update last login timestamp and IP
                db.execute(
                    "UPDATE user SET last_login = CURRENT_TIMESTAMP, last_login_ip = ? WHERE id = ?",
                    (request.remote_addr, user['id'])
                )
                
                logger.info(f"Successful login for user '{username}' from {request.remote_addr}")
                
            except sqlite3.Error as e:
                logger.error(f"Database error during login: {e}")
                return render_template('login.html', data={"error": "Login failed. Please try again."}), 500

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
    # session.clear()  # session is only valid in a request context
    
    # Path to the SQLite database file
    DATABASE = os.path.join(os.path.dirname(__file__), 'flowrite.db')

    # Always initialize DB to ensure schema exists
    init_db()

    # Start the Flask application
    # app.run(debug=True, port=5001, host='127.0.0.1')
    app.run(debug=True, port=5001, host='0.0.0.0')