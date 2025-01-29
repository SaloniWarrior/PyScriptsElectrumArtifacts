import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from collections import Counter
from tabulate import tabulate
import os

def extract_items_with_count(file_path):
    """
    Extracts unique items (hex keys or Bech32 addresses) from the file and counts their occurrences.

    Args:
        file_path (str): The path to the file containing items.

    Returns:
        Counter: A Counter object with items as keys and their counts as values.
        str: The type of items extracted (e.g., "Key" or "Address").
    """
    # Regular expressions for private keys and Bech32 addresses
    hex_key_pattern = re.compile(r'([A-Fa-f0-9]{2}\s){32,}')  # Matches hex keys (with spaces)
    bech32_address_pattern = re.compile(r'bc1[a-z0-9]{11,}')  # Matches Bech32 addresses

    item_counts = Counter()
    item_type = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            # Check for private keys
            hex_match = hex_key_pattern.search(line)
            if hex_match:
                hex_key = hex_match.group(0).replace(' ', '')  # Remove spaces
                item_counts[hex_key] += 1
                item_type = "Key"  # Indicate the item type as "Key"

            # Check for Bech32 addresses
            bech32_match = bech32_address_pattern.search(line)
            if bech32_match:
                bech32_address = bech32_match.group(0)
                item_counts[bech32_address] += 1
                item_type = "Address"  # Indicate the item type as "Address"

    return item_counts, item_type

def browse_file():
    """
    Opens a file dialog for the user to select a file.

    Returns:
        str: The selected file path.
    """
    Tk().withdraw()  # Hide the root window
    print("Please select the file to analyze...")
    file_path = askopenfilename(title="Select Key File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    return file_path

def save_output_to_file(output, total_unique_items, items_with_multiple_occurrences, items_with_one_occurrence, file_path, item_type):
    """
    Saves the output report to a file.

    Args:
        output (str): The output content to be saved.
        total_unique_items (int): The total number of unique items.
        items_with_multiple_occurrences (int): Number of items occurring more than once.
        items_with_one_occurrence (int): Number of items occurring exactly once.
        file_path (str): The path to the input file (used for generating the output file name).
        item_type (str): The type of items ("Key" or "Address").
    """
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    suffix = "_UniqueKeyReport" if item_type == "Key" else "_UniqueAddressReport"
    output_file_path = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        initialfile=f"{base_name}{suffix}.txt",
        title="Save Report As"
    )

    if output_file_path:
        with open(output_file_path, 'w') as output_file:
            output_file.write(f"Total Unique {item_type}s Found: {total_unique_items}\n")
            output_file.write(f"{item_type}s with more than one occurrence: {items_with_multiple_occurrences}\n")
            output_file.write(f"{item_type}s with only one occurrence: {items_with_one_occurrence}\n\n")
            output_file.write(output)
        print(f"Output saved to {output_file_path}")
    else:
        print("No file selected. Exiting...")

# Main function
if __name__ == "__main__":
    file_path = browse_file()
    if not file_path:
        print("No file selected. Exiting...")
    else:
        try:
            item_counts, item_type = extract_items_with_count(file_path)

            if len(item_counts) == 0:
                print("No items found. Please check the file format or content.")
            else:
                # Calculate additional statistics
                items_with_multiple_occurrences = sum(1 for count in item_counts.values() if count > 1)
                items_with_one_occurrence = sum(1 for count in item_counts.values() if count == 1)

                print(f"\nTotal unique {item_type}s found: {len(item_counts)}")
                print(f"{item_type}s with more than one occurrence: {items_with_multiple_occurrences}")
                print(f"{item_type}s with only one occurrence: {items_with_one_occurrence}\n")

                # Prepare data for tabular output
                table_data = [[index + 1, item, count] for index, (item, count) in enumerate(item_counts.items())]
                headers = ["#", f"{item_type} (Hex/Address)", "Count"]

                # Format the table as a string
                table_output = tabulate(table_data, headers=headers, tablefmt="grid")
                print(table_output)

                # Prompt the user to select where to save the output file
                save_output_to_file(
                    table_output, 
                    len(item_counts), 
                    items_with_multiple_occurrences, 
                    items_with_one_occurrence, 
                    file_path, 
                    item_type
                )

        except FileNotFoundError:
            print("The specified file was not found. Please check the path and try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
