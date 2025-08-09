import subprocess, os, re, time

def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def next_num(folder, prefix="output"):
    os.makedirs(folder, exist_ok=True)
    mx = -1
    rx = re.compile(rf"{re.escape(prefix)}(\d+)\.[A-Za-z0-9]+$")
    for f in os.listdir(folder):
        m = rx.match(f)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1

def prime_camera():
    # harmless if not running
    run(["killall", "gvfs-gphoto2-volume-monitor"])
    # save to SD card (more reliable)
    run(["gphoto2", "--set-config", "capturetarget=1"])
    # reviewtime already None from your log; leave it.

def capture_once(out_template, wait_s=8):
    # 1) trigger
    r1 = run(["gphoto2", "--trigger-capture"])
    if r1.returncode != 0:
        return False, r1.stderr.strip()
    # 2) wait for file, then download
    r2 = run([
        "gphoto2",
        f"--wait-event-and-download={wait_s}s",
        f"--filename={out_template}",
        "--force-overwrite"
    ])
    if r2.returncode != 0:
        return False, r2.stderr.strip()
    return True, r2.stdout.strip()

def main():
    folder = os.path.join(os.getcwd(), "OutputImages")
    prefix = "output"
    prime_camera()
    print("📸 Starting. Ctrl+C to stop.")
    try:
        while True:
            n = next_num(folder, prefix)
            # %C keeps the camera’s extension (JPG)
            out_tmpl = os.path.join(folder, f"{prefix}{n:04d}.%C")
            print(f"→ Capturing {prefix}{n:04d} ...")
            ok, msg = capture_once(out_tmpl, wait_s=8)
            if not ok:
                if "PTP Device Busy" in msg or "I/O in progress" in msg:
                    print("⚠️ Busy—waiting 4s and retrying once…")
                    time.sleep(4)
                    ok2, msg2 = capture_once(out_tmpl, wait_s=10)
                    if not ok2:
                        print(f"❌ Still failed: {msg2}")
                        break
                else:
                    print(f"❌ Capture failed: {msg}")
                    break
            else:
                print(f"✅ Saved to {folder}")
            time.sleep(2.0)  # small settle delay
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")

if __name__ == "__main__":
    main()
