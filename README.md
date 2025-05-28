# Flowrite
call it 'you'prep or 'up'rep, a simple website to log your repetition of ritual be it reading, gymming or anything per se


TODO:

- rename repo to Flowrite
- focus area: login option. user view login v/s logout, saving write to DB and pretty display at shelf (DONE, pretty display TBD)
- rate limiting the requests
- explore logging utils (TBD file based)
- add ambient music for focussed writing (play selected non-lyrical music, a cat companion animation watching, small element at bottom right)  [enhancement]
- rewrite pitch deck to highlight this is not finishing editor but a starting scratchpad [review]
- decide landing page, land on pitch or direct write page and show value [TBD]
- unauthenticated user visit shelf, friendly error page OR show samples of how his shelf might look (DONE, route to login)



- learn about PRAGMA statements. got db lock error which resolved using db context.
- pagination and offset when huge number of posts are saved.

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