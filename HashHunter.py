import hashlib
import multiprocessing

# 1. Generate hash from input text
def hash_text(text, algorithm="md5"):
    try:
        h = hashlib.new(algorithm)
        h.update(text.encode())
        print(f"[+] {algorithm.upper()} hash:", h.hexdigest())
    except ValueError:
        print("[-] The specified algorithm is not supported.")

# 2. Generate hash from a file
def hash_file(file_path, algorithm="sha256"):
    try:
        h = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                h.update(block)
        print(f"[+] Hash of {file_path} using {algorithm.upper()}:", h.hexdigest())
    except FileNotFoundError:
        print("[-] File not found.")
    except ValueError:
        print("[-] The specified algorithm is not supported.")

# 3. Single-core brute-force
def crack_hash_single(hash_value, wordlist_path, algorithm="md5"):
    try:
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
    except FileNotFoundError:
        print("[-] Wordlist file not found.")
    except ValueError:
        print("[-] The specified algorithm is not supported.")

# 4. Parallel brute-force helper
def check_words(chunk, hash_value, algorithm, result_queue):
    for word in chunk:
        word = word.strip()
        h = hashlib.new(algorithm)
        h.update(word.encode())
        if h.hexdigest().lower() == hash_value.lower():
            result_queue.put(word)
            return

def crack_hash_parallel(hash_value, wordlist_path, algorithm="md5"):
    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = f.readlines()

        cpu_count = multiprocessing.cpu_count()
        chunk_size = len(words) // cpu_count
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

        result_queue = multiprocessing.Queue()
        processes = []

        for chunk in chunks:
            p = multiprocessing.Process(target=check_words, args=(chunk, hash_value, algorithm, result_queue))
            processes.append(p)
            p.start()

        found = None
        for _ in processes:
            try:
                found = result_queue.get(timeout=15)
                break
            except:
                pass

        for p in processes:
            p.terminate()

        if found:
            print(f"[+] Match found: {found}")
        else:
            print("[-] No match found.")
    except FileNotFoundError:
        print("[-] Wordlist file not found.")
    except ValueError:
        print("[-] The specified algorithm is not supported.")

# === MAIN MENU ===
if __name__ == "__main__":
    while True:
        print("\n--- Hash Cracker Tool (Advanced Version) ---")
        print("1. Generate hash from text")
        print("2. Generate hash from file")
        print("3. Brute-force hash (single-core)")
        print("4. Brute-force hash (MULTI-CORE / multiprocessing)")
        print("5. Exit")

        choice = input("Select option (1-5): ")

        if choice == "1":
            text = input("Text to hash: ")
            alg = input("Hash algorithm (md5, sha1, sha256, ...): ")
            hash_text(text, alg)
        elif choice == "2":
            path = input("Full file path: ")
            alg = input("Hash algorithm (sha256, sha1, ...): ")
            hash_file(path, alg)
        elif choice == "3":
            hash_val = input("Hash value to crack: ")
            wordlist = input("Path to wordlist file: ")
            alg = input("Hash algorithm (md5, sha1, sha256): ")
            crack_hash_single(hash_val, wordlist, alg)
        elif choice == "4":
            hash_val = input("Hash value to crack: ")
            wordlist = input("Path to wordlist file: ")
            alg = input("Hash algorithm (md5, sha1, sha256): ")
            crack_hash_parallel(hash_val, wordlist, alg)
        elif choice == "5":
            print("[!] Exiting...")
            break
        else:
            print("Invalid selection!")
