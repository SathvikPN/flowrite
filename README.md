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
