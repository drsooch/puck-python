# Puck TODO List
Outline of what needs to be done for a stable Puck

### In Progress  
- **Teams.py**
  - [x] "Finalize" The team classes.
  - [x] Implement necessary methods for MVP
  - [ ] Documentation
- **Games.py**
  - [ ] Finalize Game classes (Needs finalization of all team classes)
  - [ ] Implement necessary methods for MVP
  - [ ] Documentation
- **GamesHandler.py**
  - [ ] Reimplement functions with new API (from Teams and Games)
  - [ ] Documentation
- **Utils.py**
  - [ ] Rework request to properly handle HTTP status codes and raise proper errors.
  - [ ] Cache data in requests?

### Future
- **TUI**
  - Banner Node
    - implement design
    - action handlers (where will the user go if they select a game)
  - Menu Node
    - finalize design
    - action handlers
  - Documentation
  - Individual game page ALL
  - Standings page ALL
  - Stats page ALL
- **CLI**
  - Implement remaining handlers for Puck CLI options
  - Documentation
  - Begin work on deciding new options
- **API Spinoff**
  - Debating on making the whole API separate and for use outside this project would be helpful to many (maybe).
### Notes
There are several cases where preseason or playoff games/stats that will cause failure. There are a few noted changes that need to be made, and will be when time allows.