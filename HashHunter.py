import hashlib
import multiprocessing
import os
import readline
import glob
import sys

# === Autocomplete setup ===
def complete_path(text, state):
    line = readline.get_line_buffer().split()
    if not line:
        return [c + os.sep for c in glob.glob('*')][state]
    else:
        path = text + '*'
        matches = glob.glob(path) + glob.glob(path + os.sep + '*')
        matches = [match + '/' if os.path.isdir(match) else match for match in matches]
        try:
            return matches[state]
        except IndexError:
            return None

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete_path)

# === Helpers ===
def valid_algorithm(algorithm):
    return algorithm.lower() in hashlib.algorithms_available

def get_algorithm_input(prompt="Hash algorithm (e.g. md5, sha1, sha224, sha256...): "):
    while True:
        alg = input(prompt).lower()
        if valid_algorithm(alg):
            return alg
        else:
            print(f"[-] Unsupported algorithm! Supported algorithms are: {', '.join(sorted(hashlib.algorithms_guaranteed))}")

# === 1. Hash text ===
def hash_text(text, algorithm):
    h = hashlib.new(algorithm)
    h.update(text.encode())
    print(f"[+] {algorithm.upper()} hash:", h.hexdigest())

# === 2. Hash file ===
def hash_file(file_path, algorithm):
    if not os.path.isfile(file_path):
        print("[-] File not found.")
        return
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            h.update(block)
    print(f"[+] Hash of {file_path} using {algorithm.upper()}:", h.hexdigest())

# === 3. Brute-force single core ===
def crack_hash_single(hash_value, wordlist_path, algorithm):
    if not os.path.isfile(wordlist_path):
        print("[-] Wordlist file not found.")
        return
    hash_value = hash_value.lower()
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            word = line.strip()
            h = hashlib.new(algorithm)
            h.update(word.encode())
            if h.hexdigest().lower() == hash_value:
                print(f"[+] Match found: {word} (line {line_num})")
                return
            if line_num % 100000 == 0:
                print(f"  [*] Checked {line_num} words...")
    print("[-] No match found.")

# === 4. Parallel brute-force ===
def check_words(chunk, hash_value, algorithm, result_queue):
    for word in chunk:
        word = word.strip()
        h = hashlib.new(algorithm)
        h.update(word.encode())
        if h.hexdigest().lower() == hash_value.lower():
            result_queue.put(word)
            return

def crack_hash_parallel(hash_value, wordlist_path, algorithm):
    if not os.path.isfile(wordlist_path):
        print("[-] Wordlist file not found.")
        return
    hash_value = hash_value.lower()

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        words = f.readlines()

    cpu_count = multiprocessing.cpu_count()
    chunk_size = max(1, len(words) // cpu_count)
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

    result_queue = multiprocessing.Queue()
    processes = []

    for chunk in chunks:
        p = multiprocessing.Process(target=check_words, args=(chunk, hash_value, algorithm, result_queue))
        processes.append(p)
        p.start()

    found = None
    try:
        found = result_queue.get(timeout=60)
    except:
        pass

    for p in processes:
        p.terminate()

    if found:
        print(f"[+] Match found: {found}")
    else:
        print("[-] No match found.")
        
        
banner = r"""
██╗  ██╗ █████╗ ███████╗██╗  ██╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║  ██║██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
███████║███████║███████╗███████║███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██║██╔══██║╚════██║██╔══██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║██║  ██║███████║██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                                                                                    
"""




# === MAIN MENU ===
def main():
    # ANSI escape code for bold text
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    print(banner)
    print("--- Hash Cracker Tool (Version 1.0.2) ---")
    while True:
        print(f"\n{BOLD}[ 1 ]  🛠️  Generate HASH from TEXT{RESET}")
        print(f"{BOLD}[ 2 ]  📄  Generate HASH from FILE{RESET}")
        print(f"{BOLD}[ 3 ]  🚀  Brute-force HASH (Single-Core){RESET}")
        print(f"{BOLD}[ 4 ]  ⚡  Brute-force HASH (Multi-Core){RESET}")
        print(f"{BOLD}[ 5 ]  ❌  Exit{RESET}\n")


        choice = input("Select option (1-5): ").strip()
        if choice == "1":
            text = input("Text to hash: ")
            alg = get_algorithm_input()
            hash_text(text, alg)

        elif choice == "2":
            path = input("Full file path (tab completes): ")
            alg = get_algorithm_input()
            hash_file(path, alg)

        elif choice == "3":
            hash_val = input("Hash value to crack: ")
            wordlist = input("Path to wordlist file (tab completes): ")
            alg = get_algorithm_input()
            crack_hash_single(hash_val, wordlist, alg)

        elif choice == "4":
            hash_val = input("Hash value to crack: ")
            wordlist = input("Path to wordlist file (tab completes): ")
            alg = get_algorithm_input()
            crack_hash_parallel(hash_val, wordlist, alg)

        elif choice == "5":
            print("[!] Exiting...")
            sys.exit(0)
        else:
            print("Invalid selection!")

if __name__ == "__main__":
    main()
