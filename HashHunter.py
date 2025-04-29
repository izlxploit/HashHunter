import hashlib
import multiprocessing

# 1. Mətnin hash dəyərini çıxartmaq
def hash_text(text, algorithm="md5"):
    try:
        h = hashlib.new(algorithm)
        h.update(text.encode())
        print(f"[+] {algorithm.upper()} hash:", h.hexdigest())
    except ValueError:
        print("[-] Daxil edilən alqoritm dəstəklənmir.")

# 2. Faylın hash dəyərini çıxartmaq
def hash_file(file_path, algorithm="sha256"):
    try:
        h = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                h.update(block)
        print(f"[+] {file_path} faylının {algorithm.upper()} hash:", h.hexdigest())
    except FileNotFoundError:
        print("[-] Fayl tapılmadı.")
    except ValueError:
        print("[-] Daxil edilən alqoritm dəstəklənmir.")

# 3. Tək nüvə ilə bruteforce
def crack_hash_single(hash_value, wordlist, algorithm="md5"):
    try:
        hash_value = hash_value.lower()
        with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                word = line.strip()
                h = hashlib.new(algorithm)
                h.update(word.encode())
                if h.hexdigest().lower() == hash_value:
                    print(f"[+] Tapıldı: {word} (sətir {line_num})")
                    return
                if line_num % 100000 == 0:
                    print(f"  [*] {line_num} söz yoxlandı...")
        print("[-] Heç bir uyğunluq tapılmadı.")
    except FileNotFoundError:
        print("[-] Wordlist faylı tapılmadı.")
    except ValueError:
        print("[-] Hash alqoritmi dəstəklənmir.")

# 4. Paralel bruteforce üçün alt funksiyalar
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
            print(f"[+] Tapıldı: {found}")
        else:
            print("[-] Heç bir uyğunluq tapılmadı.")
    except FileNotFoundError:
        print("[-] Wordlist faylı tapılmadı.")
    except ValueError:
        print("[-] Hash alqoritmi dəstəklənmir.")

# === ƏSAS MENYU ===
if __name__ == "__main__":
    while True:
        print("\n--- hashlib əsaslı Cyber Tool (təkmilləşdirilmiş) ---")
        print("1. Mətnin hash dəyərini çıxart")
        print("2. Faylın hash dəyərini çıxart")
        print("3. Hash dəyərini bruteforce et (tək nüvə)")
        print("4. Hash dəyərini bruteforce et (ÇOX NÜVƏ / multiprocessing)")
        print("5. Çıxış")

        secim = input("Seçim (1-5): ")

        if secim == "1":
            text = input("Mətn: ")
            alg = input("Hash alqoritmi (md5, sha1, sha256, ...): ")
            hash_text(text, alg)
        elif secim == "2":
            yol = input("Faylın tam yolu: ")
            alg = input("Hash alqoritmi (sha256, sha1, ...): ")
            hash_file(yol, alg)
        elif secim == "3":
            hash_val = input("Hash dəyəri: ")
            wordlist = input("Wordlist faylının yolu: ")
            alg = input("Hash alqoritmi (md5, sha1, sha256): ")
            crack_hash_single(hash_val, wordlist, alg)
        elif secim == "4":
            hash_val = input("Hash dəyəri: ")
            wordlist = input("Wordlist faylının yolu: ")
            alg = input("Hash alqoritmi (md5, sha1, sha256): ")
            crack_hash_parallel(hash_val, wordlist, alg)
        elif secim == "5":
            print("[!] Çıxılır...")
            break
        else:
            print("Yanlış seçim!")

