# llmsploit.py

> 🧠💥 **LLM + Metasploit automation** — control the Metasploit Framework using natural language commands powered by local Large Language Models.

---

## 📖 Overview

`llmsploit.py` is a Python tool that connects a **local LLM** (via [Ollama](https://ollama.ai) or any CLI-accessible model) to the **Metasploit RPC API**.  
It lets you type natural language like:

```
scan target 192.168.1.10 for open ports
```

…and the LLM will translate it into valid Metasploit commands, execute them through `msfrpcd`, and return results — all without leaving your terminal.

---

## ✨ Features

- 🔗 **Natural language → Metasploit** (LLM translates your instructions)  
- ⚡ Full RPC support (`use`, `set`, `exploit`, `run`, `sessions`, etc.)  
- 📝 Command history & logging  
- 🤖 Autonomous mode (`--auto`) to let the LLM plan and execute multi-step workflows  
- 🔒 Local-only by design (no cloud models needed)

---

## 🚀 Getting Started

### 1. Install prerequisites

- **Metasploit Framework**  
  ```bash
  sudo apt install metasploit-framework
  ```
  **Install Required Libraries**  
  ```bash
  pip3 install pymetasploit3
  ```
- **Start msfrpcd**  
  ```bash
  msfrpcd -U msf -P yourpassword -a 127.0.0.1
  ```
- **Ollama with a model** (e.g. `mistral`, `phi3`, `llama3`)  
  ```bash
  ollama pull mistral
  ```

### 2. Clone and run

```bash
git clone https://github.com/Te-REDSA/llmsploit.git
cd llmsploit
python3 llmsploit.py
```

---

## 🖥️ Usage

### Interactive mode

```bash
python3 llmsploit.py
```

Example:

```
You: search smb exploit
LLM Suggests: search type:exploit smb
Metasploit Output: [list of exploits...]
```

### Autonomous mode

Let the LLM plan a chain of actions:

```bash
python3 llmsploit.py --auto
```

---

## ⚠️ Disclaimer

This project is for **educational and authorized penetration testing only**.  
Running exploits against systems without permission is **illegal and unethical**.  
The author(s) take no responsibility for misuse.

---

## 🛠 Roadmap

- [ ] Web UI dashboard  
- [ ] Multi-LLM support (switch models easily)  
- [ ] Integration with session management (`post` modules, Meterpreter)  
- [ ] Config file for persistent settings  

---

## 🤝 Contributing

Pull requests, issues, and feature requests are welcome!  
If you build something cool with `llmsploit.py`, share it with the community.

---

## 📜 License

[MIT License](LICENSE)

---
