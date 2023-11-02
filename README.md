## Updates
===================================================================================
- recursive implementation of node processing to enable deeper level of nesting
  (PlantUML however does not support high level nesting of ifs, therefore big switches are implemented by switch)
- implemented loops (while, for, do while)
- implemented switch statement with case, default and break (restricted to well formed cases with break at the end)
- implemented support of constructors and destructors (linking to destructor still to do)
- changed handling of partitions to keep diagrams small

### Hints for usage
Flowgen comments must be first in line, e.g. the following will not work:

    if (x <10)
    { //$ This comment will not be processed by Flowgen
      x=10;
    }

this is ok:

    if (x <10)
    { 
      //$ This comment be processed by Flowgen
      x=10;
    }

- if flowgen produces queer results or does not put the comments at the correct branch, check for compilation errors
  - Flowgen produces some limited diagnostics from CLang at begin of the output processing of each compilation unit
  - check for missing declarations because of missing header files
  - For each processed function, Flowgen produces a node-tree. If some parts of the code are missing in that tree, 
    CLang stopped compilation because of some missing declaration or syntax error
  - including full header files from Cygwin or MinGW may cause problems. Reduced header files as in Flowgen/Flogen/inc will do.


- Comments in code excluded by if def are nevertheless processed, if the function is included in compilation
- if you need some special code for flowgen use define `__has_include`:

    #if defined(__has_include) // for Flowgen
    #include stdio.h
    #endif

===================================================================================
## FLOWGEN SOFTWARE PREREQUISITES:

- Python3 
http://www.python.org/getit/

- PlantUML (already provided; NO need to install)
http://plantuml.sourceforge.net/

- LLVM-Clang 16.0 (or superior) 
http://clang.llvm.org/

- Clang-Python3 bindings (tested with v16.0.1.1)
https://pypi.org/project/clang/


### ACKNOWLEDGMENTS:

Thanks to the PlantUML team, specially to Arnaud Roques; to cldoc’s developer, Jesse Van Den Kieboom; 
and to the big LLVM+Clang developer community. This tool would not be possible without them.


## INSTALLATION:

[FOR UNIX-LIKE SYSTEMS: MAC/LINUX]

- Install Python3 (if not present)

- Install LLVM+Clang 16.0 (or superior). 

For MAC, you may try using a package management solution such as MacPorts or Fink.
For Linux (type?), you may try using a package management solution such as…

LLVM+Clang pre-built binaries are available from
http://llvm.org/releases/download.html

After installation, the environment variable
`LD_LIBRARY_PATH=<path/to/llvm-project/build>/lib`
pointing to the libraries should have been set, or it can be set manually.
That folder contains required library files such as "libclang.dylib". 

- Download Flowgen from GitHub.


[FOR WINDOWS]

- Install Python3 (if not present)

- Install LLVM+Clang 16.0 (or superior). 

Prebuilt binaries available (3.4 or superior) from
http://llvm.org/releases/download.html
Choose the option 'Add LLVM to system PATH for all users’

- Download Flowgen from GitHub.

### TROUBLESHOOTING

- If during the execution you get the error that `libclang` is missing despite `LD_LIBRARY_PATH` being defined per instructions above, try creating a symling with the requested name. For example, in case you get 

    ````
    OSError: libclang-16.so: cannot open shared object file: No such file or directory
    ```

    Try `sudo ln -s <path/to/llvm-project/build>/lib/libclang.so.16.0.0 <path/to/llvm-project/build>/lib/libclang-16.so`.

- If you get the error about missing system includes, add the path to the headers' location inside LLVM project to the command under execution. For example,

    ```
    python3 build_db.py example/simple_demo_src.cpp -I<path/to/llvm-project/build>/lib/clang/<version>/include
    ```

## CONFIGURING AND RUNNING FLOWGEN:

There is an example in the folder EXAMPLE, with some C++ code.

### FOR UNIX-LIKE SYSTEMS: MAC/LINUX

The makefile is configured to either compile the sample program, by typing
> make a.out
or to run Flowgen and generate the documentation, by typing
> make flowdoc
The documentation is generated as .html files inside flowdoc/

Note: erase the folder flowdoc/ to regenerate completely the documentation.
Note: it may be necessary to adjust the variables FLOWGEN_DIR and CXX to run the makefile. 
Note: type ‘make’ to do both actions (compiling and generating documentation) in the same run.
Note [MAC SPECIFIC]: by default, makefiles are not recognized on Mac systems. In order to check, 
      you can do 'make --version'. If it says: ‘-bash: make: command not found’, then you should install it. 
      The easiest is to install the xCode addition to Mac OS X. 

The //$ annotations and the code can be changed in the test C++ code to experiment with Flowgen.

**TLDR**: 

- adjust the `INCLUDES` variable in the `Makefile`.
- execute `rm -rf flowdoc` to make sure the directory does not already exist.
- execute `make flowdoc 1> stdout_log.txt 2> stderr_log.txt`. The results can be found inside `flowdoc`. The standard output and errors are redirected to `stdout_log.txt` and `stderr_log.txt`, respectively.

### FOR WINDOWS

Set FLOWGEN_DIR environment variable to the FLOWGEN folder
The make batch file ‘make_WIN.bat’ is configured to run the example
The documentation is generated as .html files inside flowdoc/

NOTE: FOR THE MOMENT, the user has to copy manually the folder '/htmlCSSandJS' from the Flowgen folder
      into the /flowdoc folder of the documentation project
      This should be done automatically by make_WIN.bat

The //$ annotations and the code can be changed in the test C++ code to experiment with Flowgen.



## MAP OF FILES

```
build_db.py —> Flowgen Python3 executable
makeflows.py —> Flowgen Python3 executable
makehtml.py —> Flowgen Python3 executable
plantuml.jar —> PlantUML java executable, used by Flowgen
ToDoList.txt —> To Do list, for continued development of the open source Flowgen tool.
LICENSE.txt —> License agreement
README.txt —> Information
clang/ —> FOLDER with Clang-Python3 bindings, used by Flowgen
htmlCSSandJS/ --> FOLDER with CSS and Javascript files that are copied 
                  into the '/flowdoc' SUBFOLDER of any project by the Flowgen script, 
                  and which are needed by the output HTML files
example/  —> FOLDER with sample application
      /make_WIN.bat —> Flowgen executable for WINDOWS
      /Makefile —> Makefile for systems that have the Make utility. 
                   It can be used to compile the C++ code or to run Flowgen
      /simple_demo_src.cpp —> sample C++ source file with main() function  
      /include/ —> SUB-FOLDER with sample C++  headers
      /src/ —> SUB-FOLDER with sample C++  source files
      /flowdoc/ —> SUB-FOLDER with documentation generated by flowgen 
                   (this whole folder can be erased and regenerated via Flowgen)
              /*.html —> the output HTML documentation files
              /aux_files/ —> SUB-SUB-FOLDER with auxiliary files created by Flowgen: 
                             - database files (.flowdb)
                             - diagrams (.png), 
                             - CMAPX files which are used by the HTML output files 
                               to generate hyperlinks in the PNG diagram files.
                             - PlantUML diagram-descriptions (*.txt)  
                               (they can be used as input to PlantUML)

```

