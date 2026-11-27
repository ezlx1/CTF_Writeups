<div align="center">

<img src="assets/header.svg" alt="CTF Writeups animated header" width="100%">

<br>

![Last commit](https://img.shields.io/github/last-commit/ezlx1/CTF_Writeups?style=flat-square&color=39ff14&labelColor=0d1117)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-ezlx-39ff14?style=flat-square&labelColor=0d1117&logo=tryhackme&logoColor=white)](https://tryhackme.com/p/ezlx)
![HackTheBox](https://img.shields.io/badge/HackTheBox-ezlx1-39ff14?style=flat-square&labelColor=0d1117&logo=hackthebox&logoColor=white)
![pwn.college](https://img.shields.io/badge/pwn.college-ezlx-39ff14?style=flat-square&labelColor=0d1117)
![PortSwigger](https://img.shields.io/badge/PortSwigger-Web_Academy-39ff14?style=flat-square&labelColor=0d1117&logo=portswigger&logoColor=white)

**Notes, methodology and full exploit chains from the boxes and labs I work through.**

</div>

---

## `>_` About

I'm **Aws**, a CS graduate (TTU, 2026) heading for **junior SOC Analyst / Red Team** roles in Jordan and the MENA region.

This repo is my working notebook. Every writeup explains the *why* behind each step — what I saw, what I tried, what failed — not just the final flag. It's a work in progress, and new writeups are added as I finish them.

## `>_` Methodology

```mermaid
flowchart LR
    A[Recon] --> B[Enumeration]
    B --> C[Foothold]
    C --> D[Privilege escalation]
    D --> E[Loot / flag]
    E --> F[Writeup + lessons learned]
    C -. dead end .-> B
    D -. dead end .-> B
```

Every writeup follows the same structure: **Summary → Recon → Foothold → Escalation → Mitigation → Takeaways**.

The mitigation section matters most to me — that's the defensive (SOC) side of the same story.

## `>_` Latest Writeups

<!-- WRITEUPS:START -->
| Writeup | Platform | Difficulty | OS |
|---|---|---|---|
| [Lockdown](Tryhackme/Lockdown/README.md) | Tryhackme | Medium | Linux |
| [Anonymous Playground — TryHackMe Writeup](Tryhackme/Anonymous Playground/README.md) | Tryhackme | Hard | — |
| [TryHackMe: VulnNet](Tryhackme/VulnNet/README.md) | Tryhackme | Medium | Linux |
| [M4tr1x: Exit Denied](Tryhackme/M4tr1x Exit Denied/README.md) | Tryhackme | Hard | — |
| [Plotted-EMR — TryHackMe Writeup](Tryhackme/Plotted_EMR/README.md) | Tryhackme | — | — |
| [README](Tryhackme/Rubber Stamp/README.md) | Tryhackme | Hard | Windows |
| [Python Playground](Tryhackme/Python Playground/README.md) | Tryhackme | Hard | Linux |
| [CherryBlossom — TryHackMe Writeup](Tryhackme/CherryBlossom/README.md) | Tryhackme | — | — |
| [TryHackMe — Motunui](Tryhackme/Motunui/README.md) | Tryhackme | — | — |
<!-- WRITEUPS:END -->

## `>_` Disclaimer

For **educational purposes only**. Every target here is a purpose-built lab or CTF environment I was authorized to attack. Flags and credentials are redacted. Don't use any of this against systems you don't own or have written permission to test.

<div align="center">

**[github.com/ezlx1](https://github.com/ezlx1)**

<sub>`while true; do learn; break_stuff; document; done`</sub>

</div>
