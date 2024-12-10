# 42

A commandline tool to create, compile, debug, and run projects.

## Installation

To install 42 tools, run the following command
```sh
bash <(curl -s https://raw.githubusercontent.com/Matthias1590/42_tools/refs/heads/main/install.sh)
```

## Commands

> To get a help menu in the commandline, run `42 --help`.
> To print debug info, add `--debug` right after `42` (e.g. `42 --debug run`).

### 42 init

```sh
42 init [--force] [--libft] [--minilibx]
```

Creates a new project in the current folder. If `--force` is specified, any existing files will be deleted and the project will be reinitialized. If `--libft` is specified, your libft project will be added to the current project, your libft project should be in a folder called libft which is located in the same folder as your new project folder. If `--minilibx` is specified, minilibx will be added to the current project, minilibx should be in a folder called minilibx which is located in the same folder as your new project folder.

### 42 run

```sh
42 run [--debug] [--no-norminette] [...arguments]
```

Compiles and runs your program. If `--debug` is specified it compiles with debug info and runs with valgrind, if `--no-norminette` is specified, norminette is not ran. The arguments after the flags will be passed to the newly built executable.

### 42 compile

```sh
42 compile [--debug] [--no-norminette]
```

Compiles your program. If `--debug` is specified it compiles with debug info, if `--no-norminette` is specified, norminette is not ran.

### 42 update

```sh
42 update
```

Updates the 42 commandline tool. You will get warnings when running commands if you're using an outdated version. To check the current version run `42 --version`.
