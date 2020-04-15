# Puck TODO List
### CURRENT WORK
1. Handle parser failures better ie: consider using get()
2. When a player is scratched or injured we do not create a player object in PlayerCollection (SEE: 1)
3. Rework Async portions of puck to be under one module.
   - Make the Worker pool more maintainable.

### In Progress
- **Teams**
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
- **Database**
  - Add views for stat rankings
  - Expand queries to allow for more flexible selection

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
