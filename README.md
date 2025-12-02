# LOLCODE INTERPRETER- CMSC 124 Project ['25-'26]

**Group Name:** Cause <br/>
**Section:** ST-6L <br/>
**Members:** <br/>
 Quevin James Custodio
 Fernando IV Eugene Castro <br/>

**Contributions:**
Quevin James Custodio
 - made the lexer.py, parser.py, semantic.py and execute.py
 - helped in getting resources from online sources 
 - he facilitated the project

Fernando IV Eugene Castro
 - made the gui.py
 - fixed the error format for the lexer.py, parser.py, and semantic.py
 - made the README.md file
 - fixed the 


**LOLCODE Interpreter** </br>
**Program Description:**
This project is aN interpreter for the language LOLCODE. It is built using Python and features a complete pipeline including Lexical Analysis, Syntax Analysis (Parsing), Semantic Analysis, and Code Execution. The interpreter includes a Graphical User Interface (GUI) built with Tkinter, allowing users to write, load, analyze, and execute LOLCODE scripts in a user-friendly environment.


Key Features: <br/>
• Full Interpretation Pipeline: Implements Lexer, Parser, Semantic Analyzer, and Executor. <br/>
• GUI: shows  <br/>
• Real-time Feedback: Displays tokens, symbol tables (variable & function), and console output in dedicated panels. <br/>
• Error Handling: Provides specific error messages with line numbers for debugging.  <br/>
•  Code Editor: Includes line numbering and basic text editing features. <br/>
•  Support for LOLCODE Constructs: Handles variables, arithmetic, boolean logic, flow control (if-else, switch, loops), and functions. <br/>

**Installation Guide:** <br/>
1. Clone repository link: https://github.com/quevinjames/cmsc_124_project.git
2. Open the project folder in your preferred IDE (e.g., VS Code) and open the terminal.
3. Prerequisites **(Python & Tkinter)**:
    • Check if Python is installed:
    Type python3 --version in your terminal.

    • Check/Install Tkinter (Required for GUI):
    Tkinter usually comes pre-installed with Python. To check, run:

        python3 -m tkinter

    If a small window appears, you are good to go.

    • If missing on Linux (Ubuntu/Debian):

        sudo apt-get update
        sudo apt-get install python3-tk

    • If missing on macOS: If you installed Python via Homebrew (brew install python-tk), it should be there. Otherwise, reinstall Python from the official website, ensuring the "tcl/tk" option is checked.

<br/>

**How to Use App:** 
### 
1. Navigate to the source code directory: cd "source code"
2. Run the Main Script: python3 main.py
3. Choose Mode:
    - The terminal will ask: Run in GUI mode? (y/n):
    - Type y to launch the GUI.
    - Type n to run in CLI or basically won't run GUI.
4. In GUI Mode:
    - Click "Upload File" to load a .lol file (sample files are in the test cases folder).
    - Click "Analyze" to tokenize, parse, and execute the code.
    - View the results in the Terminal/Console Output pane at the bottom and check the lexemes, Symbol table, funtion table if there are any result.



## References
- 
<br/>

## Note to Instructor:

See the various branches in this repository to see the significant commits of other members of this group project. Thanks!
