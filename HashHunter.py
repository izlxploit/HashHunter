# HashHunter 🔐
# Multi-functional cyber security tool using hashlib
# Features: Generate hash, hash file, brute-force hash (with wordlist)

import hashlib

# 1. Generate hash from a text input
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

# 3. Brute-force a hash using a wordlist (single-threaded)
def crack_hash(hash_value, wordlist_path, algorithm="md5"):
    try:
        with open(wordlist_path, "r") as f:
            for line in f:
                word = line.strip()
                h = hashlib.new(algorithm)
                h.update(word.encode())
                if h.hexdigest() == hash_value:
                    print(f"[+] Match found: {word}")
                    return
        print("[-] No match found in the wordlist.")
    except FileNotFoundError:
        print("[-] Wordlist file not found.")
    except ValueError:
        print("[-] The specified algorithm is not supported.")

# Main menu
if __name__ == "__main__":
    while True:
        print("\n--- HashHunter Cyber Tool ---")
        print("1. Generate hash from text")
        print("2. Generate hash from file")
        print("3. Brute-force hash (with wordlist)")
        print("4. Exit")

        choice = input("Select option (1-4): ")

        if choice == "1":
            text = input("Text to hash: ")
            alg = input("Hash algorithm (md5, sha1, sha256, ...): ")
            hash_text(text, alg)
        elif choice == "2":
            file_path = input("Full file path: ")
            alg = input("Hash algorithm (sha256, sha1, ...): ")
            hash_file(file_path, alg)
        elif choice == "3":
            hash_val = input("Hash value to crack: ")
            wordlist = input("Path to wordlist file: ")
            alg = input("Hash algorithm (md5, sha1, sha256): ")
            crack_hash(hash_val, wordlist, alg)
        elif choice == "4":
            print("[!] Exiting...")
            break
        else:
            print("Invalid selection!")
