import json
import os
from pymetasploit3.msfrpc import MsfRpcClient
import subprocess
import readline
from datetime import datetime

# === Configuration ===
LLM_COMMAND = "ollama generate"
LLM_MODEL = "Mistral"
MSFRPC_PASSWORD = "YourStrongPassword"
LOG_FILE = "autonomous_msf_agent.log"

# Persistent in-memory state
history = []
targets = {}  # Stores info about scanned/exploited targets

# Connect to Metasploit RPC
try:
    client = MsfRpcClient(MSFRPC_PASSWORD)
except Exception as e:
    print(f"[!] Failed to connect to Metasploit RPC: {e}")
    exit(1)

def log_action(user_input, assistant_response, job_id=None, auto=False):
    entry = {
        "timestamp": str(datetime.now()),
        "user": user_input,
        "assistant": assistant_response,
        "job_id": job_id,
        "auto": auto
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def ask_llm(prompt):
    try:
        result = subprocess.run(
            [LLM_COMMAND, LLM_MODEL, "--prompt", prompt],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"[!] LLM error: {e}")
        return None

def execute_module(module_type, module_name, options):
    try:
        module = client.modules.use(module_type, module_name)
        for key, value in options.items():
            module[key] = value
        job_id = module.execute()
        return job_id
    except Exception as e:
        print(f"[!] Error executing module: {e}")
        return None

def list_sessions():
    return client.sessions.list

def display_sessions():
    sessions = list_sessions()
    if not sessions:
        print("[*] No active sessions")
        return
    print("[*] Active Sessions:")
    for sid, data in sessions.items():
        print(f"Session {sid} | Type: {data['type']} | Target: {data['tunnel_peer']}")

def update_targets(module_data):
    """
    Track targets that have been scanned or exploited
    """
    options = module_data.get("options", {})
    rhosts = options.get("RHOSTS") or options.get("RHOST")
    if rhosts:
        targets[rhosts] = {
            "module": module_data.get("module_name"),
            "type": module_data.get("module_type"),
            "options": options
        }

def autonomous_suggestion():
    """
    Ask LLM to suggest next logical steps based on targets and sessions
    """
    prompt = f"""
You are an expert autonomous penetration testing agent.
Here is the current state:

History: {json.dumps(history, indent=2)}
Targets: {json.dumps(targets, indent=2)}
Active sessions: {json.dumps(list_sessions(), indent=2)}

Suggest the next Metasploit module to run, 
and provide JSON with:
{{
  "module_type": "exploit|auxiliary|post|payload",
  "module_name": "<Metasploit module path>",
  "options": {{ "<option>": "<value>" }}
}}
"""
    llm_response = ask_llm(prompt)
    return llm_response

def main():
    print("[*] Autonomous LLM-Powered Metasploit Agent")
    print("[*] Type 'exit' to quit, 'sessions' to view sessions, 'summary' to summarize, 'auto' for autonomous suggestion")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "sessions":
            display_sessions()
            continue
        elif user_input.lower() == "summary":
            print("[*] Active sessions and targets summary:")
            display_sessions()
            print(json.dumps(targets, indent=2))
            continue
        elif user_input.lower() == "auto":
            llm_response = autonomous_suggestion()
            print(f"[LLM Autonomous Suggestion]:\n{llm_response}")

            try:
                module_data = json.loads(llm_response)
                module_type = module_data.get("module_type")
                module_name = module_data.get("module_name")
                options = module_data.get("options", {})

                print(f"[Auto Suggestion]: Execute {module_type}/{module_name} with options {options}")
                confirm = input("Execute this automatically? (y/n): ").strip().lower()
                if confirm == 'y':
                    job_id = execute_module(module_type, module_name, options)
                    print(f"[+] Module job started with Job ID: {job_id}")
                    log_action("autonomous", llm_response, job_id, auto=True)
                    update_targets(module_data)
                else:
                    log_action("autonomous_skipped", llm_response, None, auto=True)

                history.append({"user": "autonomous", "assistant": llm_response})

            except json.JSONDecodeError:
                print("[!] LLM did not return valid JSON.")
                log_action("autonomous", llm_response, None, auto=True)
            continue

        # === Normal conversational workflow ===
        prompt = f"""
You are an expert Metasploit assistant.
Previous actions: {json.dumps(history, indent=2)}
Instruction: {user_input}
Respond in JSON with:
{{
  "module_type": "exploit|auxiliary|post|payload",
  "module_name": "<Metasploit module path>",
  "options": {{ "<option>": "<value>" }}
}}
"""
        llm_response = ask_llm(prompt)
        if not llm_response:
            print("[!] No response from LLM")
            continue

        try:
            module_data = json.loads(llm_response)
            module_type = module_data.get("module_type")
            module_name = module_data.get("module_name")
            options = module_data.get("options", {})

            print(f"[LLM Suggests]: Execute {module_type}/{module_name} with options {options}")
            confirm = input("Execute this module? (y/n): ").strip().lower()
            if confirm == 'y':
                job_id = execute_module(module_type, module_name, options)
                print(f"[+] Module job started with Job ID: {job_id}")
                log_action(user_input, llm_response, job_id)
                update_targets(module_data)
            else:
                log_action(user_input, llm_response, None)

            history.append({"user": user_input, "assistant": llm_response})

        except json.JSONDecodeError:
            print("[!] LLM did not return valid JSON. Output:")
            print(llm_response)
            log_action(user_input, llm_response, None)

if __name__ == "__main__":
    main()
