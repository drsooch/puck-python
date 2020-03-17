# Puck TODO List
Outline of what needs to be done for a stable Puck

### CURRENT WORK
I have just finished switching over to Postgresql as the main application database. I wish I could've kept using SQLite3 as it has a light footprint however it was just not feasible. Python3 comes bundled with a version of sqlite3 that does not allow window functions (which Puck needs). I'd rather not have users go through hoops to change this bundled version.

### In Progress
- **Teams**
  - Documentation
- **Players**
  - Flesh out implementation
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
  - Begin work on deciding new options
### Notes
There are several cases where preseason or playoff games/stats that will cause failure. There are a few noted changes that need to be made, and will be when time allows.