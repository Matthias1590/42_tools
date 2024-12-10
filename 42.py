#!/bin/python3

import argparse
import os
import shutil
import logging
import yaml
import subprocess
import re

def main() -> None:
    parser = argparse.ArgumentParser(prog="42")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging", default=False)
    parser.add_argument("--version", action="version", version="%(prog)s v1.0")

    subparsers = parser.add_subparsers(dest="command")

    init = subparsers.add_parser("init", help="Set up a new project")
    init.add_argument("--libft", action="store_true", help="Include libft")
    init.add_argument("--minilibx", action="store_true", help="Include minilibx")

    compile = subparsers.add_parser("compile", help="Compile the project")
    compile.add_argument("--no-norminette", action="store_true", help="Run without norminette", default=False)
    compile.add_argument("--debug", action="store_true", help="Compile with debug flags")

    run = subparsers.add_parser("run", help="Run the project")
    run.add_argument("--no-norminette", action="store_true", help="Run without norminette", default=False)
    run.add_argument("--debug", action="store_true", help="Run with valgrind")
    run.add_argument("options", nargs=argparse.REMAINDER, help="Options to pass to the project")

    update = subparsers.add_parser("update", help="Update 42 tools")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.command == "update":
        run_update(args)
        return

    if args.command != "init":
        load_config(args)

    match args.command:
        case "init":
            run_init(args)
        case "compile":
            run_compile(args)
        case "run":
            run_run(args)

def run_update(args: argparse.Namespace) -> None:
    run_command(f"cd {os.path.dirname(__file__)!r} && git pull")

def run_init(args: argparse.Namespace) -> None:
    if args.libft:
        include_libft()
    if args.minilibx:
        include_minilibx()
    create_folders(args)
    create_makefile(args)
    create_gitignore(args)
    create_config(args)

    logging.info("Project initialized successfully")

def include_libft() -> None:
    include_project(get_libft_path(), "libft")

def get_libft_path() -> str:
    return find_folder("libft")

def include_project(path: str, target: str) -> None:
    logging.debug(f"Including project {target} from {path}")
    shutil.copytree(path, target)

    if os.path.exists(os.path.join(target, ".git")):
        logging.debug(f"Included project {target} contains .git folder, removing it")
        shutil.rmtree(os.path.join(target, ".git"))

    logging.debug(f"Included project {target} successfully")

def include_minilibx() -> None:
    include_project(get_minilibx_path(), "minilibx")

def get_minilibx_path() -> str:
    return find_folder("minilibx")

def find_folder(target: str) -> str:
    logging.debug(f"Finding {target} folder")

    current_path = os.getcwd()
    while current_path != "/":
        parent_path = os.path.dirname(current_path)
        target_path = os.path.join(parent_path, target)

        logging.debug(f"Checking {target_path}")
        if os.path.exists(target_path):
            logging.debug(f"{target} folder found at {target_path}")
            return target_path

        current_path = parent_path

    raise Exception(f"{target} folder not found")

def create_makefile(args: argparse.Namespace, warn_if_exists: bool = True) -> bool:
    logging.debug("Creating Makefile")

    modified = False

    old_makefile = None
    if os.path.exists("Makefile"):
        old_makefile = read_file("Makefile")

        if warn_if_exists:
            logging.warning("Deleting existing Makefile")
            os.remove("Makefile")
            modified = True

    with open("Makefile", "w") as f:
        f.write(f"""
# Generated using 42 tools, manual changes may be overwritten

## Commands ##

CC = cc
CFLAGS = {get_c_flags(args)}
LDFLAGS = {get_ld_flags(args)}
RM = rm -f

## Files ##

SRCS = {get_sources()}
OBJS = $(SRCS:src/%.c=obj/%.o)

## Configuration ##

NAME = {get_project_name(args)}

## Compilation rules ##

$(NAME): $(OBJS) {get_libs(args)}
\t$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

obj/%.o: src/%.c
\t$(CC) $(CFLAGS) -c -o $@ $<

## Cleaning rules ##

clean:
{get_clean_commands(args)}

fclean: clean
{get_fclean_commands(args)}

re: fclean $(NAME)
{get_re_commands(args)}

{get_lib_rules(args)}
"""[1:])  # TODO: run clean, fclean, and re for included libraries as well

    logging.debug("Makefile created/updated successfully")

    if args.libft:
        if update_libft_makefile(args):
            modified = True
    if args.minilibx:
        if update_minilibx_makefile(args):
            modified = True
    
    if not old_makefile or old_makefile != read_file("Makefile"):
        modified = True

    return modified

def get_clean_commands(args: argparse.Namespace) -> str:
    commands = "\t$(RM) $(OBJS)\n"

    if args.libft:
        commands += """
\t$(MAKE) -C libft clean
"""[1:]
    if args.minilibx:
        commands += """
\t$(MAKE) -C minilibx clean
"""[1:]
    
    return commands.rstrip()

def get_fclean_commands(args: argparse.Namespace) -> str:
    commands = "\t$(RM) $(OBJS) $(NAME)\n"

    if args.libft:
        commands += """
\t$(MAKE) -C libft fclean
"""[1:]
    if args.minilibx:
        commands += """
\t$(MAKE) -C minilibx clean
"""[1:]

    return commands.rstrip()

def get_re_commands(args: argparse.Namespace) -> str:
    commands = ""

    if args.libft:
        commands += """
\t$(MAKE) -C libft re
"""[1:]
    if args.minilibx:
        commands += """
\t$(MAKE) -C minilibx re
"""[1:]
        
    return commands.rstrip()

def update_libft_makefile(args: argparse.Namespace) -> bool:
    logging.debug("Updating libft Makefile")

    return update_makefile("libft/Makefile", args)

def update_minilibx_makefile(args: argparse.Namespace) -> bool:
    logging.debug("Updating minilibx Makefile")

    return update_makefile("minilibx/Makefile.mk", args)

def update_makefile(path: str, args: argparse.Namespace) -> bool:
    logging.debug(f"Updating {path} Makefile")

    makefile = read_file(path)
    old_makefile = makefile

    matches = re.findall(r"^CFLAGS\s*(:|\?|)=\s*(.*)$", makefile, re.MULTILINE)
    if not matches:
        logging.error(f"Could not find CFLAGS in {path}, cannot compile with debug flags")
        return
    match = matches[0]
    
    cflags = match[1].strip()
    if ("debug" in args and args.debug) and "-g" not in cflags:
        cflags = f"{cflags} -g".strip()
    elif not ("debug" in args and args.debug) and "-g" in cflags:
        cflags = cflags.replace("-g", "").strip()

    makefile = re.sub(r"^CFLAGS\s*(:|\?|)=\s*(.*)$", f"CFLAGS {match[0]}= {cflags}", makefile, flags=re.MULTILINE)

    if makefile != old_makefile:
        write_file(path, makefile)
        logging.debug(f"Makefile updated")
        return True
    else:
        logging.debug(f"Makefile not modified")
        return False

def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)

def get_libs(args: argparse.Namespace) -> str:
    libs = ""
    if args.libft:
        libs += " libft/libft.a"
    if args.minilibx:
        libs += " minilibx/libmlx.a"
    return libs.strip()

def get_lib_rules(args: argparse.Namespace) -> str:
    rules = ""

    if args.libft:
        rules += """
libft/libft.a:
\t$(MAKE) -C libft

"""[1:]
    if args.minilibx:
        rules += """
minilibx/libmlx.a:
\t$(MAKE) -C minilibx

"""[1:]
        
    if rules:
        rules = "## Libraries ##\n\n" + rules

    return rules.strip()

def get_c_flags(args: argparse.Namespace) -> str:
    c_flags = "-Wall -Wextra -Werror -I./includes"
    if "debug" in args and args.debug:
        c_flags += " -g"
    if args.libft or args.minilibx:
        c_flags += " -I./"
    return c_flags.strip()

def get_ld_flags(args: argparse.Namespace) -> str:
    ld_flags = ""

    if args.libft:
        ld_flags += " -L./libft -lft"
    if args.minilibx:
        ld_flags += " -L./minilibx -lmlx -lX11 -lXext -lm"

    return ld_flags.strip()

def get_sources() -> str:
    return " ".join([file for file in get_all_files("src") if file.endswith(".c")])

def get_all_files(path: str) -> list[str]:
    files = []

    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            files += get_all_files(os.path.join(path, file))
        else:
            files.append(os.path.join(path, file))

    return files

def get_project_name(args: argparse.Namespace) -> str:
    return os.path.basename(os.getcwd())

def create_gitignore(args: argparse.Namespace) -> None:
    logging.debug("Creating .gitignore")

    with open(".gitignore", "w") as f:
        f.write("""
# Generated using 42 tools, manual changes may be overwritten

# IDE files
.vscode

# Compiled files
*.o
"""[1:])

    logging.debug(".gitignore created successfully")

def create_folders(args: argparse.Namespace) -> None:
    logging.debug("Creating folders")

    os.makedirs("src", exist_ok=True)
    os.makedirs("includes", exist_ok=True)
    os.makedirs("obj", exist_ok=True)

    logging.debug("Folders created successfully")

def create_config(args: argparse.Namespace) -> None:
    logging.debug("Creating config file")

    with open(".42_config.yml", "w") as f:
        yaml.dump({
            "libft": args.libft,
            "minilibx": args.minilibx,
        }, f)
    
    logging.debug("Config file created successfully")

def load_config(args: argparse.Namespace) -> None:
    logging.debug("Loading config file")

    if not os.path.exists(".42_config.yml"):
        logging.error("Project has not yet been initialized or the config file has been deleted, please run `42 init`")
        exit(1)

    with open(".42_config.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    args.libft = config["libft"]
    args.minilibx = config["minilibx"]

    logging.debug("Config file loaded successfully")

def run_compile(args: argparse.Namespace) -> bool:
    logging.debug("Running compile")

    modified = create_makefile(args, warn_if_exists=False)

    if "no_norminette" not in args or not args.no_norminette:
        run_norminette()

    copy_source_structure()
    if run_make(args, modified):
        logging.info("Project compiled successfully")
        return True
    else:
        logging.error("Project failed to compile")
        return False

def copy_source_structure() -> None:
    logging.debug("Copying source structure to obj folder")

    for file in get_all_files("src"):
        if file.endswith(".c"):
            obj_dir = os.path.dirname(file.replace("src", "obj"))
            os.makedirs(obj_dir, exist_ok=True)

    logging.debug("Source structure copied successfully")

def run_norminette() -> bool:
    logging.debug("Running norminette")

    res = run_command("norminette src includes", check_result=False)

    if res:
        logging.debug("Norminette passed")
    else:
        logging.debug("Norminette failed")

    return res

def run_make(args: argparse.Namespace, force_rebuild: bool = False) -> bool:
    logging.debug("Running make")

    command = "make"
    if force_rebuild:
        command += " -B"

    res = run_command(command, check_result=False)

    if res:
        logging.debug("Make passed")
    else:
        logging.debug("Make failed")

    return res

def run_command(command: str, check_result: bool = True) -> bool:
    logging.debug(f"Running command: {command}")

    res = subprocess.run(command, shell=True, check=check_result)

    if check_result:
        logging.debug("Command completed successfully")
    else:
        logging.debug("Command completed")
    
    return res.returncode == 0

def run_run(args: argparse.Namespace) -> None:
    logging.debug("Compiling and running project")

    if not run_compile(args):
        return

    if args.debug:
        run_valgrind(args)
    else:
        run_project(args)

def run_valgrind(args: argparse.Namespace) -> None:
    logging.debug("Running valgrind")

    options = " ".join([f"'{opt}'" for opt in args.options])

    run_command(f"valgrind ./{get_project_name(args)} {options}")

def run_project(args: argparse.Namespace) -> None:
    logging.debug("Running project")

    options = " ".join([f"'{opt}'" for opt in args.options])

    run_command(f"./{get_project_name(args)} {options}")

if __name__ == "__main__":
    main()
