import os
import re
from tkinter import Tk, filedialog
from mnemonic import Mnemonic
from collections import Counter

def load_bip39_wordlist():
    """
    Loads the BIP-39 wordlist from a predefined path or prompts the user to select it.

    Returns:
        list: A list of 2048 words.
    """
    Tk().withdraw()  # Hide the root window
    wordlist_file = filedialog.askopenfilename(title="Select BIP-39 Wordlist File", filetypes=[("Text files", "*.txt")])
    if not wordlist_file:
        raise FileNotFoundError("No BIP-39 wordlist file selected.")

    with open(wordlist_file, 'r') as file:
        return [word.strip() for word in file.readlines()]

def validate_seed_phrase_with_checksum(seed_phrase):
    """
    Validates a seed phrase using the BIP-39 checksum validation.

    Args:
        seed_phrase (str): The seed phrase to validate.

    Returns:
        bool: True if the seed phrase passes checksum validation, False otherwise.
    """
    mnemo = Mnemonic("english")
    return mnemo.check(seed_phrase)

def extract_seed_phrases_from_dump(dump_file_path, wordlist, progress_file_path):
    """
    Extracts potential seed phrases from a memory dump by matching against the BIP-39 wordlist.
    Resumes from the last processed position if interrupted.

    Args:
        dump_file_path (str): Path to the memory dump file.
        wordlist (list): List of BIP-39 words.
        progress_file_path (str): Path to the file where progress is saved.

    Returns:
        list: A list of validated seed phrases found in the memory dump.
    """
    seed_phrases = []
    total_size = os.path.getsize(dump_file_path)
    processed_size = 0

    # Check if progress file exists, if so, resume from the last saved position
    if os.path.exists(progress_file_path):
        with open(progress_file_path, 'r') as progress_file:
            processed_size = int(progress_file.read().strip())
        print(f"Resuming from {processed_size} bytes.")
    else:
        print("Starting fresh extraction.")

    # Compile regex pattern for matching BIP-39 words
    word_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in wordlist) + r')\b')

    with open(dump_file_path, 'rb') as dump_file:
        dump_file.seek(processed_size)  # Skip already processed part
        for chunk in iter(lambda: dump_file.read(1024 * 1024), b''):  # Process in 1MB chunks
            processed_size += len(chunk)
            print(f"Progress: {processed_size / total_size:.2%} of memory dump analyzed", end="\r")
            try:
                data = chunk.decode(errors='ignore')  # Decode chunk into string
            except UnicodeDecodeError:
                continue

            # Extract potential phrases by matching words
            potential_phrases = re.findall(word_pattern, data)

            # Check for valid seed phrases of 12, 18, or 24 words
            for length in [12, 18, 24]:
                for i in range(len(potential_phrases) - length + 1):
                    phrase = ' '.join(potential_phrases[i:i + length])
                    if validate_seed_phrase_with_checksum(phrase):
                        seed_phrases.append(phrase)

            # Save progress after each chunk
            with open(progress_file_path, 'w') as progress_file:
                progress_file.write(str(processed_size))

    print("\nExtraction and analysis complete.")
    return list(set(seed_phrases))  # Remove duplicates

def browse_file():
    """
    Opens a file dialog to select the memory dump file.

    Returns:
        str: The file path of the selected memory dump file.
    """
    Tk().withdraw()  # Hide the root window
    dump_file_path = filedialog.askopenfilename(title="Select Memory Dump File")
    if not dump_file_path:
        raise FileNotFoundError("No file selected.")
    return dump_file_path

def save_log_file(seed_phrases, input_file, save_directory):
    """
    Saves the extracted seed phrases to a log file with their occurrence counts.

    Args:
        seed_phrases (list): List of extracted seed phrases.
        input_file (str): The path of the input memory dump file.
        save_directory (str): The directory where the report should be saved.
    """
    output_file_name = os.path.basename(input_file).rsplit('.', 1)[0] + "_SeedPhraseReport.txt"
    save_path = os.path.join(save_directory, output_file_name)

    # Count occurrences of each seed phrase using Counter
    phrase_counts = Counter(seed_phrases)

    # Create the report content
    report_content = [
        "Valid Seed Phrases Extracted from Memory Dump\n",
        "-" * 100,
        f"Seed Phrases Found:\n"
    ]

    # Add table headers
    report_content.append(f"{'No.':<5} {'Seed Phrase and Occurrence Count'}\n")
    report_content.append("-" * 100)

    # Add each seed phrase and its occurrence count in the same column
    for idx, (phrase, count) in enumerate(phrase_counts.items(), 1):
        report_content.append(f"{idx:<5} {phrase:<80} | {count:<5}")

    # Write the report content to the file
    with open(save_path, 'w') as output_file:
        output_file.write("\n".join(report_content))

    print(f"Seed phrases saved to {save_path}")

# Main script
if __name__ == "__main__":
    try:
        # Ask the user for paths to the necessary files
        print("Select the BIP-39 wordlist file.")
        bip39_wordlist = load_bip39_wordlist()

        print("Select the memory dump file.")
        dump_file_path = browse_file()

        print("Select the directory where the progress and log files should be saved.")
        Tk().withdraw()  # Hide the root window
        save_directory = filedialog.askdirectory(title="Select Directory for Saving Files")
        if not save_directory:
            raise FileNotFoundError("No directory selected.")

        # Define the progress tracking file
        progress_file_path = os.path.join(save_directory, "progress.txt")

        print("Extracting seed phrases from the memory dump...")
        seed_phrases = extract_seed_phrases_from_dump(dump_file_path, bip39_wordlist, progress_file_path)

        if seed_phrases:
            print(f"\nFound {len(seed_phrases)} valid seed phrases:")
            for idx, phrase in enumerate(seed_phrases, 1):
                print(f"{idx}: {phrase}")

            print("Saving the seed phrase report...")
            save_log_file(seed_phrases, dump_file_path, save_directory)
        else:
            print("\nNo valid seed phrases found in the memory dump.")

    except Exception as e:
        print(f"Error: {e}")
