import re
import base58
import hashlib
import os

# Updated regex pattern for stricter WIF private key matching
wif_key_pattern = re.compile(r'[LK][1-9A-HJ-NP-Za-km-z]{51}')  # Matches 52-char keys starting with L or K

# Function to validate WIF private keys
def is_valid_wif_key(wif_key):
    try:
        decoded = base58.b58decode(wif_key)
        if len(decoded) not in (33, 34):  # 33 for uncompressed, 34 for compressed keys
            return False
        payload, checksum = decoded[:-4], decoded[-4:]
        expected_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        return checksum == expected_checksum
    except Exception:
        return False

# Function to extract WIF private keys with progress and enhanced precision
def extract_wif_private_keys(file_path, chunk_size=50 * 512 * 1024):
    private_keys = []
    invalid_keys = 0
    try:
        file_size = os.path.getsize(file_path)
        print(f"Starting analysis of file: {file_path} ({file_size / (1024 * 1024):.2f} MB)")

        with open(file_path, 'rb') as f:
            processed_bytes = 0  # Track progress
            chunk_index = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                processed_bytes += len(chunk)
                chunk_index += 1
                progress = (processed_bytes / file_size) * 100
                print(f"[Chunk {chunk_index}] Processed: {processed_bytes / (1024 * 1024):.2f} MB "
                      f"({progress:.2f}% complete)")

                decoded_chunk = chunk.decode('latin-1', errors='ignore')
                potential_keys = wif_key_pattern.findall(decoded_chunk)

                if potential_keys:
                    print(f"  Found {len(potential_keys)} potential WIF keys in chunk {chunk_index}")

                for key in potential_keys:
                    if is_valid_wif_key(key):
                        print(f"    Valid WIF private key found: {key}")
                        private_keys.append(key)
                    else:
                        print(f"    Invalid WIF private key: {key}")
                        invalid_keys += 1

        print("Analysis complete.")
        print(f"Valid WIF keys found: {len(private_keys)}")
        print(f"Invalid WIF keys encountered: {invalid_keys}")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
    return private_keys

# Main execution
if __name__ == "__main__":
    # Define inputs here
    file_path = "/media/sf_D_DRIVE/Newfolder/win10_install.mem"  # Replace with your memory dump file path
    chunk_size_kb = 512  # Set chunk size in KB (default 512 KB)
    chunk_size = chunk_size_kb * 1024  # Convert to bytes

    print(f"File path: {file_path}")
    print(f"Chunk size: {chunk_size_kb} KB")
    # Extract WIF keys
    private_keys = extract_wif_private_keys(file_path, chunk_size)

    # Final output
    if private_keys:
        print("\nExtracted valid WIF private keys:")
        for key in private_keys:
            print(key)
    else:
        print("\nNo valid WIF private keys found.")
