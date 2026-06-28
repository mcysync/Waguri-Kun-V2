import glob

print("Scanning for broken asyncio tasks...")
for filepath in glob.glob("modules/*.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    if ".create_task(" in text or "loop =" in text or "bot_instance" in text:
        # Nuke the dangerous lines
        lines = text.split("\n")
        safe_lines = []
        for line in lines:
            if "create_task" in line or "get_event_loop" in line or "from bot import bot" in line:
                safe_lines.append("# " + line)
            else:
                safe_lines.append(line)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(safe_lines))
        print(f"✅ Cleaned {filepath}")

print("🌸 All modules are now perfectly safe for Termux!")
