# FocusLock — System-Level Productivity Enforcer

A desktop focus enforcement utility designed to restrict digital distractions, lock foreground task workflows, and eliminate dopamine-trap applications during deep-work sprints.

## Core Features
- **Application & Website Blocking:** Restricts unauthorized background processes and domains during active lockouts.
- **Configurable Work Sprints:** Dynamic session parameters managed via centralized JSON preferences.
- **Standalone Binary Packaging:** Automated toolchain for generating single-executable Windows binaries via PyInstaller.

## Files
- `FocusLock.py`: Primary application event loop, UI window, and process enforcement logic.
- `fl_config.json`: Configuration state, timer parameters, and task limits.
- `BUILD_EXE.bat`: Packaging automation script for standalone Windows distribution.

## License
MIT License
