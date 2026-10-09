"""
Local AI agent using Ollama with conversation memory and switchable models.

Setup:
    pip install -U ollama
    ollama serve          # if not already running
    python agent.py

Commands inside the chat:
    /models          list the models installed on your computer
    /model <name>    switch model (offers to download it if not installed)
    /reset           forget the conversation (also clears the saved file)
    /history         show how many messages are remembered
    /exit            quit (memory is saved automatically)

Memory is shared across models: switch models mid-chat and the new one
still sees everything you talked about.
"""

import ast
import json
import operator
import os
import re
from datetime import datetime

import ollama

DEFAULT_MODEL = "llama3.1:latest"
HISTORY_FILE = "chat_history.json"   # memory persists here between runs
CONFIG_FILE = "agent_config.json"    # remembers the last model you used
MAX_MESSAGES = 40                    # keep the last N messages (plus system prompt)
KEEP_ALIVE = "30m"                   # keep the model loaded in RAM between messages

# Small free models that run well on a laptop (try: /model llama3.2:3b)
SUGGESTED = ["llama3.2:3b", "qwen2.5:3b", "gemma2:2b", "phi3:mini", "mistral"]

# Tools are only attached when the message looks like it needs them (much faster on CPU)
TOOL_HINTS = re.compile(
    r"\b(time|date|day|today|clock|calculate|calc|sum|plus|minus|times|divided)\b"
    r"|\d\s*[-+*/^%]\s*\d",
    re.IGNORECASE,
)

SYSTEM_PROMPT = (
    "You are a helpful assistant running locally. "
    "Remember everything the user tells you in this conversation. "
    "Use the tools when they help (current time, math). Be concise."
)

STATE = {"model": DEFAULT_MODEL}


# ---------------------------------------------------------------- tools
def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %H:%M:%S")


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculate(expression: str) -> str:
    """Evaluate a math expression such as '12 * (3 + 4) / 2'.

    Args:
        expression: The math expression to evaluate.
    """
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Error: {e}"


TOOL_FUNCS = {"get_current_time": get_current_time, "calculate": calculate}


# --------------------------------------------------------------- memory
def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_history(messages: list) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def trim(messages: list) -> list:
    """Keep the system prompt + the most recent messages."""
    system, rest = messages[0], messages[1:]
    rest = rest[-MAX_MESSAGES:]
    while rest and rest[0]["role"] != "user":   # don't start mid tool-call
        rest.pop(0)
    return [system] + rest


# -------------------------------------------------------- model manager
def load_saved_model() -> str:
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("model") or DEFAULT_MODEL
    except (OSError, json.JSONDecodeError):
        return DEFAULT_MODEL


def save_saved_model(name: str) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"model": name}, f)


def installed_models() -> list:
    """Names of models installed in Ollama (works with old and new ollama versions)."""
    resp = ollama.list()
    items = getattr(resp, "models", None)
    if items is None and isinstance(resp, dict):
        items = resp.get("models", [])
    names = []
    for m in items or []:
        if isinstance(m, dict):
            name = m.get("model") or m.get("name")
        else:
            name = getattr(m, "model", None) or getattr(m, "name", None)
        if name:
            names.append(name)
    return names


def resolve_model(name: str, installed: list):
    """Match 'llama3.2' to 'llama3.2:3b' etc. Returns the exact name or None."""
    if name in installed:
        return name
    if f"{name}:latest" in installed:
        return f"{name}:latest"
    matches = [m for m in installed if m.split(":")[0] == name]
    return matches[0] if len(matches) == 1 else None


def pull_model(name: str) -> bool:
    """Download a model with a simple progress display."""
    print(f"Downloading {name} (this can take a while)...")
    try:
        for p in ollama.pull(name, stream=True):
            status = getattr(p, "status", "") or ""
            done, total = getattr(p, "completed", None), getattr(p, "total", None)
            if done and total:
                print(f"\r  {status}: {done * 100 // total}%   ", end="", flush=True)
            else:
                print(f"\r  {status}                    ", end="", flush=True)
        print("\nDownload complete.")
        return True
    except KeyboardInterrupt:
        print("\nDownload cancelled.")
    except Exception as e:
        print(f"\nCould not download '{name}': {e}")
    return False


def show_models() -> None:
    try:
        installed = installed_models()
    except Exception as e:
        print(f"Could not reach Ollama: {e}\n")
        return
    print("Installed models:")
    for m in installed:
        print(f"  {'*' if m == STATE['model'] else ' '} {m}")
    print("  (* = in use)")
    print("Free models you can download with /model <name>: " + ", ".join(SUGGESTED) + "\n")


def switch_model(name: str) -> None:
    if not name:
        print(f"Current model: {STATE['model']}. Usage: /model <name>\n")
        return
    try:
        installed = installed_models()
    except Exception as e:
        print(f"Could not reach Ollama: {e}\n")
        return

    target = resolve_model(name, installed)
    if target is None:
        answer = input(f"'{name}' is not installed. Download it now? (y/n): ").strip().lower()
        if answer != "y" or not pull_model(name):
            print("Model not changed.\n")
            return
        target = resolve_model(name, installed_models()) or name

    old = STATE["model"]
    if target != old:
        try:   # free the old model's RAM so two models don't sit in memory
            ollama.generate(model=old, prompt="", keep_alive=0)
        except Exception:
            pass
    STATE["model"] = target
    save_saved_model(target)
    print(f"Switched to {target}. Memory is kept. The first reply may be slow while it loads.\n")


# ---------------------------------------------------------------- agent
def run_turn(messages: list, use_tools: bool) -> str:
    """Send messages to the model, run any tool calls, return the final answer."""
    while True:
        kwargs = {"tools": list(TOOL_FUNCS.values())} if use_tools else {}
        try:
            resp = ollama.chat(model=STATE["model"], messages=messages,
                               keep_alive=KEEP_ALIVE, **kwargs)
        except ollama.ResponseError as e:
            # some models (e.g. phi3, gemma2) cannot use tools: retry as plain chat
            if use_tools and "tool" in str(e).lower():
                print(f"  [{STATE['model']} does not support tools - answering without them]")
                use_tools = False
                continue
            raise
        msg = resp.message

        entry = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            entry["tool_calls"] = [
                {"function": {"name": c.function.name,
                              "arguments": dict(c.function.arguments)}}
                for c in msg.tool_calls
            ]
        messages.append(entry)

        if not msg.tool_calls:
            return msg.content

        for call in msg.tool_calls:
            name = call.function.name
            func = TOOL_FUNCS.get(name)
            try:
                result = func(**call.function.arguments) if func else f"Unknown tool: {name}"
            except Exception as e:
                result = f"Tool error: {e}"
            print(f"  [tool] {name}({dict(call.function.arguments)}) -> {result}")
            messages.append({"role": "tool", "tool_name": name, "content": str(result)})


def main():
    STATE["model"] = load_saved_model()
    messages = load_history()
    print(f"Agent ready ({STATE['model']}). Remembered messages: {len(messages) - 1}")
    print("Type /models, /model <name>, /reset, /history or /exit. "
          "Ctrl+C while thinking cancels the reply.\n")

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user == "/exit":
            break
        if user == "/reset":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            save_history(messages)
            print("Memory cleared.\n")
            continue
        if user == "/history":
            print(f"{len(messages) - 1} messages remembered.\n")
            continue
        if user == "/models":
            show_models()
            continue
        if user == "/model" or user.startswith("/model "):
            try:
                switch_model(user[len("/model"):].strip())
            except (KeyboardInterrupt, EOFError):
                print("\nModel not changed.\n")
            continue

        checkpoint = len(messages)               # to roll back if the turn fails
        messages.append({"role": "user", "content": user})
        print("Agent is thinking...", flush=True)
        try:
            answer = run_turn(messages, bool(TOOL_HINTS.search(user)))
        except KeyboardInterrupt:
            del messages[checkpoint:]            # remove the half-finished turn
            print("\nCancelled.\n")
            continue
        except Exception as e:
            del messages[checkpoint:]
            print(f"Error talking to Ollama: {e}\n")
            continue

        messages[:] = trim(messages)
        save_history(messages)
        print(f"Agent [{STATE['model']}]: {answer}\n")

    save_history(messages)
    print("Bye! Memory saved to", HISTORY_FILE)


if __name__ == "__main__":
    main()
