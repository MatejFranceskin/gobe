# MushroomCards Executable Distribution

## What was created

A completely self-contained Windows executable `MushroomCards.exe` has been created in the `dist` folder. This executable:

- **Single file distribution** - Everything bundled into one .exe file
- **No external dependencies** - Database and font files are embedded inside the executable
- **Optimized performance** - Uses efficient resource loading for faster operation
- **Cross-machine compatibility** - Can run on any Windows computer (Windows 7+) without Python

The build process automatically embeds:
- **Python runtime and all libraries**
- **gobe.db** - The mushroom database (embedded inside the .exe)
- **arialuni.ttf** - Unicode font for proper Slovenian character rendering (embedded inside the .exe)

## File Requirements

**Just one file!** 

- **MushroomCards.exe** - The complete standalone application

All required resources are now embedded inside the executable using PyInstaller's data bundling.

## Distribution Instructions

**Super simple distribution:**

1. Copy `MushroomCards.exe` to any Windows computer
2. Double-click to run - that's it!

No additional files, folders, or setup required. The application will automatically extract and use the embedded database and font files.

## Rebuilding the Executable

If you make changes to `cards_gui.py`, you can rebuild the executable by:

1. Running the batch file: `build_executable.bat`
2. Or manually running: `python -m PyInstaller --onefile --windowed --name "MushroomCards" --add-data "gobe.db;." cards_gui.py`

## File Sizes and Performance

- The executable will be larger (around 30-50 MB) because it contains Python and all libraries
- First startup might be slightly slower than running the Python script directly
- Once loaded, performance should be identical to the Python script

## System Requirements

- Windows 7 or later (64-bit)
- No Python installation required
- No additional libraries needed

## Troubleshooting

If the executable doesn't work on the target computer:

1. Make sure `gobe.db` is in the same folder as the .exe
2. Check that the target computer has Windows 7 or later
3. Try running from command prompt to see any error messages
4. Ensure the user has permission to run .exe files in that location
