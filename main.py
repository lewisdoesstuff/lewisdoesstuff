import gifos

# Initialize the Terminal object
t = gifos.Terminal(
    width=800,
    height=600,
    xpad=5,
    ypad=5,
    font_size=15,
)

# Set the frames per second
t.set_fps(15)


# Function to print a line of boot text with color
def boot_line(text, row, delay=2, color="white", contin=False, save=True):
    t.set_txt_color(color)
    t.gen_text(text=text, row_num=row, contin=contin)
    t.clone_frame(delay)
    if save:
        t.save_frame(base_file_name=f"frame_{row}")
    t.set_txt_color("white")


# Function to print a line of init text with color
def init_line(text, row, save=True):
    t.gen_text("[ ", row_num=row)
    t.set_txt_color("green")
    t.gen_text("OK", row_num=row, contin=True)
    t.set_txt_color("white")
    t.gen_text(" ] ", row_num=row, contin=True)
    t.gen_text(text=text, row_num=row, contin=True)
    if save:
        t.save_frame(base_file_name=f"frame_{row}")


# Function to print `.. Done` with color
def print_dots_done(row, delay=2):
    boot_line(".", row, delay, contin=True)
    boot_line(".", row, delay, contin=True)
    boot_line(".", row, delay, contin=True)
    boot_line(" Done", row, delay, contin=True, color="green")


# Simulate the boot process
boot_line("lemmons ltd bios.js initializing", 1, delay=5)
print_dots_done(1)
boot_line("Hardware detection", 3, delay=2)
print_dots_done(3)

boot_line("Hardware detected:", 4)
boot_line("  CPU: js.core/V8 Compatible rendering engine", 5, delay=2)
boot_line("  RAM: 256MiB", 6, delay=2)
boot_line("  Display: 800x600 16-bit color GitHub Markdown Renderer", 7, delay=2)
t.clone_frame(15)

boot_line("Beginning memory test...", 9, delay=4)

# Memory test simulation
for i in range(0, 262144, 8192):  # 256MiB Memory
    t.delete_row(9)
    t.gen_text(f"Beginning memory test... {i}KiB", 9)

t.delete_row(9)
boot_line(f"Beginning memory test...", 9)
boot_line(" 262144KiB OK", 9, color="green", contin=True)
t.clone_frame(15)

t.clear_frame()

# Simulate the kernel boot process
boot_line("lemmons ltd kernel.js initializing", 1)
print_dots_done(1)
init_line("Starting system...", 2)
init_line("Initializing hardware...", 3)
init_line("Checking filesystems...", 4)
init_line("Mounting volumes...", 5)
init_line("Starting networking service...", 6)
init_line("Initializing display...", 7)
t.gen_text("Welcome to lew's profile!", 9)
t.clone_frame(15)
t.clear_frame()

# Simulate login prompt
t.set_font("CascadiaCodePL.ttf", 15)
t.gen_text(text="github login: ", row_num=1)
t.gen_typing_text(text="lewisdoesstuff", row_num=1, col_num=14, contin=True, speed=0.1)
t.clone_frame(10)
t.gen_text(text="Password: ", row_num=2)
t.gen_typing_text(text="********", row_num=2, col_num=10, contin=True, speed=0.1)
t.clone_frame(15)

t.clear_frame()
t.gen_text(text="Welcome, lewisdoesstuff! Last Login: 01-01-1970T00:00:01", row_num=1)
t.set_prompt("\x1b[35mlewisdoesstuff\x1b[39m@\x1b[32mgithub\x1b[39m:~$ ")
t.gen_prompt(2)
t.gen_typing_text(text="ghfetch -u lewisdoesstuff", row_num=2, contin=True, speed=0.1)

gh_stats = gifos.utils.fetch_github_stats("lewisdoesstuff")
details_lines = f"""\x1b[96mUser Rating: \x1b[93m{gh_stats.user_rank.level}\x1b[0m
\x1b[96mTotal Stars Earned: \x1b[93m{gh_stats.total_stargazers}\x1b[0m
\x1b[96mTotal Commits (2023): \x1b[93m{gh_stats.total_commits_last_year}\x1b[0m
\x1b[96mTotal PRs: \x1b[93m{gh_stats.total_pull_requests_made}\x1b[0m
\x1b[96mMerged PR %: \x1b[93m{gh_stats.pull_requests_merge_percentage}\x1b[0m
\x1b[96mTotal Contributions: \x1b[93m{gh_stats.total_repo_contributions}\x1b[0m
"""
t.gen_text(text=details_lines, row_num=3)

t.gen_prompt(9)
t.gen_typing_text(
    text="cat /proc/languages | head -n 4", row_num=9, contin=True, speed=0.1
)
t.gen_text(text="\x1b[34mTypeScript", row_num=10)
t.gen_text(text="\x1b[33mJavaScript", row_num=11)
t.gen_text(text="\x1b[34mPython", row_num=12)
t.gen_text(text="\x1b[32mC#", row_num=13)

t.gen_prompt(14)
t.gen_typing_text(
    text="cat /proc/frameworks | head -n 2", row_num=14, contin=True, speed=0.1
)
t.gen_text(text="\x1b[32mVue", row_num=15)
t.gen_text(text="\x1b[36mTailwindCSS", row_num=16)

t.gen_prompt(17)
t.gen_typing_text(
    text='echo "thanks for stopping by!" | cowsay', row_num=17, contin=True, speed=0.3
)
cowsay_output = r"""
 _________________________ 
< thanks for stopping by! >
 ------------------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""

t.gen_text(text=cowsay_output, row_num=18, contin=True)
t.gen_prompt(26)
t.clone_frame(60)
t.gen_typing_text("reboot", 26, contin=True, speed=0.1)
t.clone_frame(5)
t.clear_frame()
init_line("Stopping system...", 1)
t.clone_frame(10)
t.clear_frame()
boot_line("System halted.", 1)
t.clone_frame(10)

# Generate the GIF
t.gen_gif()
