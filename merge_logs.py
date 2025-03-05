import pandas as pd
import re
from datetime import datetime

# Define the file paths for the three log files.
file_vm1 = "logs/probability/trial5/machine_1.log"
file_vm2 = "logs/probability/trial5/machine_2.log"
file_vm3 = "logs/probability/trial5/machine_3.log"

def parse_log_file(filepath, vm_id):
    """
    Parse a log file and return a list of dictionaries with these keys:
      - 'Global Time': the detailed time portion (HH:MM:SS.microseconds) from the timestamp.
      - 'Event': event description (text before the first '|')
      - 'Logical Clock': numeric value extracted from the log (if present)
      - 'Length of Queue': numeric value extracted from the log (if present)
      - 'VM_ID': the vm_id provided
    """
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Expected format:
            # [2025-03-05 03:59:59.532396] Some event description | Logical Clock: <num> | Length of Queue: <num>
            m = re.match(r'\[(.*?)\]\s*(.*)', line)
            if not m:
                continue  # Skip lines that don't match the expected format
            timestamp_str = m.group(1).strip()
            rest = m.group(2).strip()
            # Parse the timestamp; use a format that supports microseconds.
            try:
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            # Extract only the time portion with full microsecond precision.
            global_time = dt.strftime("%H:%M:%S.%f")  # e.g., "03:59:59.532396"

            # Split the remaining text on the "|" character.
            parts = [p.strip() for p in rest.split("|")]
            event_desc = parts[0] if len(parts) > 0 else ""
            logical_clock = ""
            length_of_queue = ""
            if len(parts) > 1:
                # Remove "Logical Clock:" text.
                logical_clock = parts[1].replace("Logical Clock:", "").strip()
            if len(parts) > 2:
                # Remove "Length of Queue:" text.
                length_of_queue = parts[2].replace("Length of Queue:", "").strip()
            # Convert numeric values if possible.
            try:
                logical_clock = float(logical_clock) if logical_clock else None
            except ValueError:
                logical_clock = None
            try:
                length_of_queue = float(length_of_queue) if length_of_queue else None
            except ValueError:
                length_of_queue = None

            data.append({
                "Global Time": global_time,
                "Event": event_desc,
                "Logical Clock": logical_clock,
                "Length of Queue": length_of_queue,
                "VM_ID": vm_id
            })
    return data

# Parse each log file with its corresponding VM_ID.
data_vm1 = parse_log_file(file_vm1, 1)
data_vm2 = parse_log_file(file_vm2, 2)
data_vm3 = parse_log_file(file_vm3, 3)

# Combine the data from all three VMs.
all_data = data_vm1 + data_vm2 + data_vm3
df = pd.DataFrame(all_data)

# Create new columns for each VM: only the matching VM_ID gets the Logical Clock value.
df['VM_1'] = df.apply(lambda row: row['Logical Clock'] if row['VM_ID'] == 1 else "", axis=1)
df['VM_2'] = df.apply(lambda row: row['Logical Clock'] if row['VM_ID'] == 2 else "", axis=1)
df['VM_3'] = df.apply(lambda row: row['Logical Clock'] if row['VM_ID'] == 3 else "", axis=1)

# Reorder columns to the desired order:
# Global Time, Event, Logical Clock, Length of Queue, VM_ID, VM_1, VM_2, VM_3
df = df[['Global Time', 'Event', 'Logical Clock', 'Length of Queue', 'VM_ID', 'VM_1', 'VM_2', 'VM_3']]

# Save the combined DataFrame to a new CSV file.
output_filename = "Probability-Trial5.csv"
df.to_csv(output_filename, index=False)
print(f"Combined log saved to {output_filename}")

# Optional: Print the first few rows for verification.
print(df.head())