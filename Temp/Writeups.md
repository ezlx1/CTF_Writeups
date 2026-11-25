<%*
// ── Templater prompts ──────────────────────────────────────────────
// Ask only what we can't infer. Press Esc / leave blank to skip a field.
const boxName    = tp.file.title;
const platform   = await tp.system.prompt("Platform (THM / HTB / Other)", "TryHackMe");
const difficulty = await tp.system.prompt("Difficulty (Easy / Medium / Hard / Insane)", "Medium");
const ip         = await tp.system.prompt("Target IP", "10.10.XX.XX");
const osType     = await tp.system.suggester(["Linux", "Windows"], ["Linux", "Windows"], false, "Target OS");
const tagsRaw    = await tp.system.prompt("Extra tags (space separated, no #)", "");
const extraTags  = tagsRaw ? tagsRaw.split(" ").filter(t => t.length).map(t => "#" + t).join(" ") + " " : "";
-%>
#writeup #<% platform.toLowerCase() %> #<% osType.toLowerCase() %> <% extraTags %>

# <% boxName %>

> **Platform:** <% platform %>
> **Difficulty:** <% difficulty %>
> **OS:** <% osType %>
> **Target IP:** `<% ip %>`
> **Date:** <% tp.date.now("YYYY-MM-DD") %>

## Introduction

Welcome to my writeup for <% platform %>'s **<% boxName %>**. <!-- One or two sentences: what the box teaches / what makes it interesting. -->

### Table of Contents
- [Scanning](#scanning)
- [Enumeration](#enumeration)
- [Gaining a Foothold](#gaining-a-foothold)
- [Privilege Escalation](#privilege-escalation)
- [Conclusion](#conclusion)

---

## Scanning

<!-- nmap / rustscan output -->

```bash
nmap -sC -sV -p- -oN nmap/initial.txt <% ip %>
```

![](Tryhackme/Motunui/Attachments/NmapScan.png)

**Open ports:**

| Port | Service | Version |
|------|---------|---------|
|      |         |         |

---

## Enumeration

### Web Enumeration
<!-- gobuster / feroxbuster / ffuf, source review, technology fingerprinting -->

![](Tryhackme/M4tr1x%20Exit%20Denied/Attachments/HomePage.png)

### Other Services
<!-- SMB, FTP, SNMP, etc. -->

---

## Gaining a Foothold

<!-- Exploitation steps leading to an initial shell: creds found, CVE exploited, upload vuln, etc. -->

![](Attachments/InitialAccess.png)

**User flag:**

```
cat /home/<user>/user.txt
```

![](Attachments/userFlag.png)

---

## Privilege Escalation

### Enumeration
<!-- linpeas / SUID binaries / sudo -l / cron jobs / kernel version -->

### Exploitation
<!-- The actual privesc path and commands used -->

**Root flag:**

```
cat /root/root.txt
```

![](Attachments/rootFlag.png)

---

## Conclusion

What I learned/practiced in this room:

-
-
-

Thank you for reading!
