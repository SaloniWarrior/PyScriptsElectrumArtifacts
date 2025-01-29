import re

def search_for_electrum_xprv_keys(data_chunk):
    """
    Searches for Electrum master private key (xprv format) patterns in a chunk of memory data.
    """
    # Regular expression pattern for Electrum master private key (xprv format)
    xprv_pattern = re.compile(r'xprv[a-km-zA-HJ-NP-Z1-9]{107,108}')
    
    # Find all potential keys in the chunk
    potential_keys = xprv_pattern.findall(data_chunk)
    
    return potential_keys

def search_in_memory_dump(file_path, chunk_size=50*512 * 1024, overlap_size=100):
    """
    Reads a memory dump file in chunks, searches for Electrum master private keys (xprv), and refines the results.
    """
    try:
        with open(file_path, 'rb') as f:
            last_chunk = b''  # To handle overlaps between chunks
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Add the last chunk's overlap to the current chunk
                chunk = last_chunk + chunk
                try:
                    # Convert chunk to string for regex search
                    decoded_chunk = chunk.decode(errors='ignore')
                except UnicodeDecodeError:
                    continue  # Skip chunk if it can't be decoded

                # Search for Electrum xprv keys in the chunk
                keys_found = search_for_electrum_xprv_keys(decoded_chunk)

                if keys_found:
                    print("Potential Electrum master private keys (xprv) found:")
                    for key in keys_found:
                        print(key)
                
                # Keep the last part of the current chunk as the new overlap
                last_chunk = chunk[-overlap_size:]
    
    except MemoryError:
        print("MemoryError: The memory dump file is too large to process in memory.")
    
    except Exception as e:
        print(f"Error: {e}")

# Path to your memory dump file
memory_dump_file = '/media/sf_D_DRIVE/Newfolder/win10_install.mem'

# Run the search function with chunk size set to 1 MB and overlap size to 100 bytes
search_in_memory_dump(memory_dump_file, chunk_size=1024 * 1024, overlap_size=100)
