import os
import re
import sys
from datetime import datetime, timezone

from chrome import THEMES, render_gif

FPS = 15
# Let the GitHub page show through the terminal body instead of the scheme's background
TRANSPARENT_BODY = True

# Usage: python main.py [dark|light]
mode = sys.argv[1] if len(sys.argv) > 1 else "dark"
theme = THEMES[mode]

# gifos reads its config on import, so the color scheme must be set first
os.environ["GIFOS_GENERAL_COLOR_SCHEME"] = theme["scheme"]
if TRANSPARENT_BODY:
    # Draw onto the page color so anti-aliased text edges blend with it
    os.environ[f"GIFOS_{theme['scheme'].upper()}_DEFAULT_COLORS_BG"] = theme["page"]

import gifos

# ANSI colors, resolved by gifos to the active color scheme
RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN = (f"\x1b[3{i}m" for i in range(1, 7))
LABEL, VALUE, RESET = "\x1b[96m", "\x1b[93m", "\x1b[39m"

OK = f"[  {GREEN}OK{RESET}  ]"
FAILED = f"[{RED}FAILED{RESET}]"
PROMPT = f"{MAGENTA}lewisdoesstuff{RESET}@{GREEN}github{RESET}:~$ "

KERNEL = "6.11.0-lemmons"
DISTRO = "lemmons linux"

# Initialize the Terminal object
t = gifos.Terminal(
    width=800,
    height=600,
    xpad=5,
    ypad=5,
    font_size=15,
)

# Set the frames per second
t.set_fps(FPS)
t.set_prompt(PROMPT)

# Row of the last printed line; gifos scrolls once we write past the bottom
row = 0


def clear():
    global row
    t.clear_frame()
    row = 0


def println(text=" ", delay=0):
    """Print a line below the previous one, like a console would."""
    global row
    row = min(row + 1, t.num_rows)
    t.gen_text(text=text, row_num=row)
    t.clone_frame(delay)


def print_block(lines, delay=0):
    """Print several lines in a single frame. They must fit on screen without scrolling."""
    global row
    t.gen_text(text="\n".join(lines), row_num=row + 1)
    row += len(lines)
    t.clone_frame(delay)


def rewrite(text, delay=0):
    """Replace the last printed line, for progress counters and spinners."""
    t.delete_row(row)
    t.gen_text(text=text, row_num=row)
    t.clone_frame(delay)


def command(text, speed=0.1, delay=5):
    """Type a command at a fresh shell prompt."""
    global row
    row = min(row + 1, t.num_rows)
    t.gen_prompt(row)
    t.gen_typing_text(text=text, row_num=row, contin=True, speed=speed)
    t.clone_frame(delay)


def dots_done(text, delay=2):
    println(text, delay)
    for dots in (".", "..", "..."):
        rewrite(text + dots, delay)
    rewrite(f"{text}... {GREEN}Done{RESET}", delay)


def start_job(unit, description, seconds=4):
    """systemd's bouncing `[ *** ]` spinner while a slow unit starts."""
    positions = [
        "*     ", "**    ", "***   ", " ***  ", "  *** ", "   ***", "    **", "     *",
    ]
    positions += positions[-2:0:-1]
    println()
    for i in range(seconds * FPS // 2):
        stars = positions[i % len(positions)]
        elapsed = i * 2 // FPS + 1
        rewrite(
            f"[{RED}{stars}{RESET}] A start job is running for {description} "
            f"({elapsed}s / 1min 30s)",
            delay=1,
        )
    rewrite(f"{OK} Started {description} ({unit}).", delay=2)


# BIOS POST
println("lemmons ltd bios.js v1.0", delay=5)
println()
dots_done("Hardware detection")
println("Hardware detected:")
println("  CPU: js.core/V8 Compatible rendering engine", delay=2)
println("  RAM: 256MiB", delay=2)
println("  Display: 800x600 16-bit color GitHub Markdown Renderer", delay=15)
println()

# Memory test simulation
println("Beginning memory test...", delay=4)
for i in range(0, 262144, 8192):  # 256MiB Memory
    rewrite(f"Beginning memory test... {i}KiB")
rewrite(f"Beginning memory test... {GREEN}262144KiB OK{RESET}", delay=10)
println()
dots_done("Booting from Hard Disk 0")
t.clone_frame(10)
clear()

# Kernel log
kernel_log = [
    (0.000000, f"Linux version {KERNEL} (lew@github) (gcc 14.2.0) #1 SMP PREEMPT_DYNAMIC"),
    (0.000000, f"Command line: BOOT_IMAGE=/vmlinuz-{KERNEL} root=/dev/gh0 ro quiet"),
    (0.000000, "BIOS-provided physical RAM map:"),
    (0.000000, "DMI: lemmons ltd GitHub Markdown Renderer, BIOS bios.js 01/01/1970"),
    (0.004123, "Memory: 262144K/262144K available"),
    (0.031337, "smpboot: CPU0: js.core/V8 Compatible rendering engine (family: 0x6)"),
    (0.118274, "PCI: Using configuration type 1 for base access"),
    (0.241930, "NET: Registered PF_INET protocol family"),
    (0.302117, "octokit: GitHub API v4 (GraphQL) bridge registered"),
    (0.412883, "usb 1-1: new high-speed USB device number 2 using xhci_hcd"),
    (0.587210, "fbcon: githubfb (fb0) is primary device"),
    (0.590014, "Console: switching to colour frame buffer device 100x37"),
    (0.873456, "EXT4-fs (gh0): mounted filesystem with ordered data mode"),
    (1.024567, "Run /sbin/init as init process"),
]
for timestamp, message in kernel_log:
    println(f"[{timestamp:12.6f}] {message}")
t.clone_frame(5)

# systemd
println()
println(f"Welcome to {BLUE}{DISTRO}{RESET}!", delay=8)
println()
println(f"{OK} Created slice Slice /system/getty.", delay=2)
println(f"{OK} Reached target Local File Systems.", delay=2)
println("         Starting Journal Service...", delay=3)
rewrite(f"{OK} Started Journal Service.", delay=2)
println(f"{OK} Mounted /home/lewisdoesstuff.", delay=2)
println("         Starting Network Manager...", delay=4)
rewrite(f"{OK} Started Network Manager.", delay=2)
println(f"{OK} Reached target Network.", delay=2)
start_job("ghstatsd.service", "GitHub Stats Daemon")
println(f"{FAILED} Failed to start Coffee Machine Service.", delay=2)
println("See 'systemctl status coffee.service' for details.", delay=6)
println(f"{OK} Started Getty on tty1.", delay=2)
println(f"{OK} Reached target Login Prompts.", delay=2)
println(f"{OK} Reached target Multi-User System.", delay=15)
clear()

# getty login on tty1
t.set_font("CascadiaCodePL.ttf", 15)
println()
println(f"{DISTRO} {KERNEL} (tty1)")
println()
println("github login: ", delay=5)
t.gen_typing_text(text="lewisdoesstuff", row_num=row, contin=True, speed=0.1)
t.clone_frame(5)
# Passwords aren't echoed, so just let the cursor sit there for a moment
println("Password: ")
t.gen_text(text="", row_num=row, contin=True, count=20)
last_login = datetime.now(timezone.utc).strftime("%a %b %e %H:%M:%S")
println(f"Last login: {last_login} on tty1", delay=10)

# Fetch-style stats, with neofetch's Linux logo beside them
command("ghfetch", delay=3)
gh_stats = gifos.utils.fetch_github_stats("lewisdoesstuff")

# Copied from neofetch (MIT): https://github.com/dylanaraps/neofetch
NEOFETCH_LINUX = r"""
${c2}        #####
${c2}       #######
${c2}       ##${c1}O${c2}#${c1}O${c2}##
${c2}       #${c3}#####${c2}#
${c2}     ##${c1}##${c3}###${c1}##${c2}##
${c2}    #${c1}##########${c2}##
${c2}   #${c1}############${c2}##
${c2}   #${c1}############${c2}###
${c3}  ##${c2}#${c1}###########${c2}##${c3}#
${c3}######${c2}#${c1}#######${c2}#${c3}######
${c3}#######${c2}#${c1}#####${c2}#${c3}#######
${c3}  #####${c2}#######${c3}#####
"""
# neofetch's `set_colors fg 8 3`, with white rather than fg so the belly stays
# light on the light theme too
logo_colors = {"${c1}": "\x1b[37m", "${c2}": "\x1b[90m", "${c3}": YELLOW}
logo = []
for line in NEOFETCH_LINUX.strip("\n").splitlines():
    width = len(re.sub(r"\$\{c\d\}", "", line))
    for token, color in logo_colors.items():
        line = line.replace(token, color)
    logo.append(line + " " * (24 - width))

info = [
    PROMPT.removesuffix(":~$ "),
    "-" * len("lewisdoesstuff@github"),
    f"{LABEL}OS{RESET}: {DISTRO} {KERNEL}",
    f"{LABEL}User Rating{RESET}: {VALUE}{gh_stats.user_rank.level}",
    f"{LABEL}Total Stars Earned{RESET}: {VALUE}{gh_stats.total_stargazers}",
    f"{LABEL}Commits (past year){RESET}: {VALUE}{gh_stats.total_commits_last_year}",
    f"{LABEL}Total PRs{RESET}: {VALUE}{gh_stats.total_pull_requests_made}",
    f"{LABEL}Merged PR %{RESET}: {VALUE}{gh_stats.pull_requests_merge_percentage}",
    f"{LABEL}Total Contributions{RESET}: {VALUE}{gh_stats.total_repo_contributions}",
    "",
    "".join(f"\x1b[{c}m███" for c in range(30, 38)),
]
info += [""] * (len(logo) - len(info))
print_block([f"{art}{line}{RESET}" for art, line in zip(logo, info)], delay=45)

command("cat /proc/languages | head -n 4")
println(f"{BLUE}TypeScript")
println(f"{YELLOW}JavaScript")
println(f"{BLUE}Python")
println(f"{GREEN}C#", delay=15)

command("cat /proc/frameworks | head -n 2")
println(f"{GREEN}Vue")
println(f"{CYAN}TailwindCSS", delay=15)

command('echo "thanks for stopping by!" | cowsay', speed=0.3)
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
for line in cowsay_output.strip("\n").splitlines():
    println(line)
row = min(row + 1, t.num_rows)
t.gen_prompt(row)
t.clone_frame(60)
t.gen_typing_text("reboot", row, contin=True, speed=0.1)
t.clone_frame(5)
clear()

# systemd shutdown, then back to the BIOS when the GIF loops
for line in [
    "Stopped target Multi-User System.",
    "Stopped GitHub Stats Daemon.",
    "Stopped Network Manager.",
    "Unmounted /home/lewisdoesstuff.",
    "Reached target System Reboot.",
]:
    println(f"{OK} {line}", delay=2)
println("reboot: Restarting system", delay=10)
clear()
t.clone_frame(10)

# Wrap the frames in window chrome and generate the GIF
render_gif(
    frames_dir="frames",
    out_path=f"output-{mode}.gif",
    mode=mode,
    title="lewisdoesstuff - GitHub",
    font_path="CascadiaCodePL.ttf",
    fps=FPS,
    transparent_body=TRANSPARENT_BODY,
)
