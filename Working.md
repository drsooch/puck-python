# Puck TODO List
Outline of what needs to be done for a stable Puck

### CURRENT WORK
I have just finished switching over to Postgresql as the main application database. I wish I could've kept using SQLite3 as it has a light footprint however it was just not feasible. Python3 comes bundled with a version of sqlite3 that does not allow window functions (which Puck needs). I'd rather not have users go through hoops to change this bundled version.

### In Progress
- **Teams**
  - TeamSeasonStats -> add some new parser functionality from URL.STANDINGS endpoint (Last 10, Streak etc.)
  - Documentation
- **Players**
  - Documentation
- **Games**
  - Documentation
- **GamesHandler**
  - Documentation
- **Utils**
  - Documentation
- **TUI**
  - Implement Single Game display

### Future
- **TUI**
  - Documentation
  - Standings page ALL
  - Stats page ALL
- **CLI**
  - Implement remaining handlers for Puck CLI options
  - Documentation
- **Proper Setup Script**
  - Currently running into issues with having psql set up the database. 

### Notes
With the NHL season coming to a halt, there may be hidden bugs that pop up in the future. My testing involves using data queried from live events. Without these events I may miss some functionality i.e. a game preview may provide certain JSON branches that results in an exception during use. 
