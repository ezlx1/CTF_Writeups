<div align="center">

<img src="assets/header.svg" alt="CTF Writeups: animated terminal header" width="100%">

<br>

![Last commit](https://img.shields.io/github/last-commit/ezlx1/CTF_Writeups?style=flat-square&color=39ff14&labelColor=0d1117)
![TryHackMe](https://img.shields.io/badge/TryHackMe-writeups-39ff14?style=flat-square&labelColor=0d1117&logo=tryhackme&logoColor=white)
![HackTheBox](https://img.shields.io/badge/HackTheBox-writeups-39ff14?style=flat-square&labelColor=0d1117&logo=hackthebox&logoColor=white)
![PortSwigger](https://img.shields.io/badge/PortSwigger-Web_Academy-39ff14?style=flat-square&labelColor=0d1117&logo=portswigger&logoColor=white)
![pwn.college](https://img.shields.io/badge/pwn.college-writeups-39ff14?style=flat-square&labelColor=0d1117)

**Notes, methodology and full exploit chains from the boxes and labs I work through.**

</div>

---

## `>_` About

I'm **Aws**, a CS graduate (TTU, 2026) heading for **junior SOC Analyst / Red Team** roles in Jordan and the MENA region.

This repo is my working notebook. Every writeup explains the *why* behind each step (what I saw, what I tried, what failed), not just the final flag. It's a work in progress, and new writeups are added as I finish them.

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

The mitigation section matters most to me, since that's the defensive (SOC) side of the same story.

## `>_` Disclaimer

For **educational purposes only**. Every target here is a purpose-built lab or CTF environment I was authorized to attack. Flags and credentials are redacted. Don't use any of this against systems you don't own or have written permission to test.

<div align="center">

**[github.com/ezlx1](https://github.com/ezlx1)**

<sub>`while true; do learn; break_stuff; document; done`</sub>

</div>
