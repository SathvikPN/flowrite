# Flowrite
Flowrite is a minimalist distraction free write space perfect for your first draft.  
Not an editor, rather a clean write space focussed on bringout out your thoughts into words. 


TODO:

- rename repo to Flowrite (done)
- focus area: login option. user view login v/s logout, saving write to DB and pretty display at shelf (DONE)
- rate limiting the requests (done)
- explore logging utils (review)
- add ambient music for focussed writing (play selected non-lyrical music, a cat companion animation watching, small element at bottom right)  [enhancement]
- rewrite pitch deck to highlight this is not finishing editor but a starting scratchpad (done)
- decide landing page, land on pitch or direct write page and show value (done)
- unauthenticated user visit shelf, friendly error page OR show samples of how his shelf might look (DONE, route to login)



- learn about PRAGMA statements. got db lock error which resolved using db context.
- pagination and offset when huge number of posts are saved. (review)

# SQLite Database Files Explained

- **flowrite.db**  
  This is the main SQLite database file. It stores all your tables, data, and schema.

- **flowrite.db-wal**  
  This is the Write-Ahead Log (WAL) file. When SQLite is in WAL mode, all changes are first written to this file for better concurrency and performance. The changes are later merged into the main database file.

- **flowrite.db-shm**  
  This is the shared memory file used by SQLite in WAL mode. It helps coordinate access and caching between different database connections.

**Summary:**  
- `flowrite.db` — main database  
- `flowrite.db-wal` — recent changes (write-ahead log)  
- `flowrite.db-shm` — shared memory for coordination

You should keep all three files together for the database to work correctly in WAL mode.



## Testing 

- visitor see first time welcome screen. description and footer sticky to bottom and no overlaps. both screens (desktop and smartphone)
- start writing > write page 
- export working with all whitespace newlines preserved
- shelf or login takes to login page
- TODO: logs are crowded, multiple logs.
- invalid login username password error fine
- register page mismatched pwd fine. 
- proper register > login page
- logged in user sees his username in welcome message
- view past posts in shelf
- export post. save post to shelf, list post chronologically decreasing order
- edit > write space loaded with post, whitespace indentations preserved
- updated post updates existing post
- logout resets page to fresh view
- write space remember font selection. font list are intentionally few.
- responsive on smartphone screens

A Flask-based writing application optimized for PythonAnywhere deployment.

## Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd flowrite
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Development Server**
   ```bash
   # This will automatically initialize the development database
   python run_dev.py
   ```

The development server will run at `http://127.0.0.1:5001` with:
- Debug mode enabled
- Auto-reload on code changes
- Development database at `instance/flowrite_dev.db`
- Detailed error pages

## PythonAnywhere Deployment

1. **Create PythonAnywhere Account**
   - Sign up at [www.pythonanywhere.com](https://www.pythonanywhere.com)
   - Note your username

2. **Upload Code to PythonAnywhere**
   ```bash
   # In PythonAnywhere bash console
   git clone <your-repo-url>
   cd flowrite
   ```

3. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Initialize Production Database**
   ```bash
   python3
   >>> from app import init_db
   >>> init_db()
   >>> exit()
   ```

5. **Configure Web App**
   - Go to Web tab → Add new web app
   - Choose "Manual Configuration"
   - Python Version: 3.9 or higher
   - Update WSGI file with:
     ```python
     # Replace YOUR_USERNAME with your PythonAnywhere username
     project_home = '/home/YOUR_USERNAME/flowrite'
     ```

6. **Set Environment Variables**
   In Web tab → Environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secure-secret-key
   ```

7. **Configure Static Files**
   In Web tab → Static files:
   ```
   URL: /static/
   Directory: /home/YOUR_USERNAME/flowrite/static/
   ```

8. **Set File Permissions**
   ```bash
   chmod 755 /home/YOUR_USERNAME/flowrite
   chmod -R 755 /home/YOUR_USERNAME/flowrite/instance
   chmod 644 /home/YOUR_USERNAME/flowrite/instance/flowrite.db
   ```

9. **Update Configuration**
   Edit `config.py`:
   ```python
   # Replace YOUR_USERNAME with your PythonAnywhere username
   DATABASE = '/home/YOUR_USERNAME/flowrite/instance/flowrite.db'
   ```

10. **Reload Application**
    - Click "Reload" in Web tab
    - Visit: `YOUR_USERNAME.pythonanywhere.com`

## Project Structure
```
flowrite/
├── app.py              # Main application file
├── config.py          # Configuration settings
├── pa_wsgi.py         # PythonAnywhere WSGI configuration
├── run_dev.py         # Local development server
├── requirements.txt   # Project dependencies
├── instance/         # Instance-specific files
│   ├── flowrite.db   # Production database
│   ├── flowrite_dev.db # Development database
│   └── logs/        # Application logs
└── static/          # Static files
```

## Development vs Production
- **Development**:
  - Uses `flowrite_dev.db`
  - Debug mode enabled
  - Detailed error pages
  - HTTP allowed
  - Runs on localhost:5001

- **Production**:
  - Uses `flowrite.db`
  - Debug mode disabled
  - Generic error pages
  - HTTPS required
  - Runs on PythonAnywhere

## Maintenance
- Logs: `instance/logs/`
- Database backups: Regularly backup `instance/flowrite.db`
- Log rotation: 7 days retention
- Monitor: PythonAnywhere Web tab → Log files

## Testing Checklist
- visitor see first time welcome screen. description and footer sticky to bottom and no overlaps. both screens (desktop and smartphone)
- start writing > write page 
- export working with all whitespace newlines preserved
- shelf or login takes to login page
- TODO: logs are crowded, multiple logs.
- invalid login username password error fine
- register page mismatched pwd fine. 
- proper register > login page
- logged in user sees his username in welcome message
- view past posts in shelf
- export post. save post to shelf, list post chronologically decreasing order
- edit > write space loaded with post, whitespace indentations preserved
- updated post updates existing post
- logout resets page to fresh view
- write space remember font selection. font list are intentionally few.
- responsive on smartphone screens
