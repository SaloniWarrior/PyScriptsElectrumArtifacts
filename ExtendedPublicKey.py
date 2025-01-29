import re

def search_for_zpub_keys(data_chunk):
    """
    Searches for zpub keys in a chunk of data.
    """
    # Regular expression pattern for zpub keys (starts with 'zpub' followed by 107 or 108 Base58 characters)
    zpub_pattern = re.compile(r'(zpub[a-km-zA-HJ-NP-Z1-9]{107,108})')
    
    # Find all potential zpub keys in the data chunk
    potential_keys = zpub_pattern.findall(data_chunk)
    
    return potential_keys

def search_in_memory_dump_for_zpub(file_path, chunk_size= 50*512 * 1024, overlap_size=100):
    """
    Reads a memory dump file in chunks, searches for zpub keys, and prints the results.
    """
    try:
        with open(file_path, 'rb') as f:
            last_chunk = b''  # Used for overlapping chunks
            key_count = 0     # Counter for found keys
            
            while True:
                # Read a chunk of the file
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Combine last chunk overlap with the current chunk
                combined_chunk = last_chunk + chunk
                
                try:
                    # Convert chunk to string for regex search
                    decoded_chunk = combined_chunk.decode(errors='ignore')
                except UnicodeDecodeError:
                    continue  # Skip non-decodable chunks

                # Search for zpub keys in the current chunk
                keys_found = search_for_zpub_keys(decoded_chunk)

                # Print any keys found
                if keys_found:
                    print("Potential zpub keys found:")
                    for key in keys_found:
                        print(key)
                        key_count += 1

                # Update the last chunk for overlap
                last_chunk = combined_chunk[-overlap_size:]
            
            if key_count == 0:
                print("No zpub keys found in the memory dump.")
            else:
                print(f"Total zpub keys found: {key_count}")

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")
    except Exception as e:
        print(f"Error: {e}")

# Path to your memory dump file
memory_dump_file = '/media/sf_F_DRIVE/W102_Tx_D2_D1_T5UnCnf_1000Satoshi.mem'

# Run the search function with chunk size set to 512 KB and overlap size to 100 bytes
search_in_memory_dump_for_zpub(memory_dump_file, chunk_size=512 * 1024, overlap_size=100)
