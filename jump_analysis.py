import pandas as pd

# Read the combined log CSV (adjust the filename if needed)
df = pd.read_csv("trial1.csv")

# Make sure the Logical Clock column is numeric (if it's not already)
df['Logical Clock'] = pd.to_numeric(df['Logical Clock'], errors='coerce')

# Initialize a dictionary to hold the average jump per VM
average_jumps = {}

# Process each VM separately.
# We assume the 'VM_ID' column indicates the machine (e.g. 1, 2, 3).
for vm in sorted(df['VM_ID'].unique()):
    # Get the rows for this VM where a Logical Clock value is present
    vm_df = df[(df['VM_ID'] == vm) & (df['Logical Clock'].notna())].copy()
    
    # Compute the difference between consecutive logical clock values.
    # The .diff() method gives NaN for the first row, so those are ignored.
    vm_df['jump'] = vm_df['Logical Clock'].diff()
    
    # Calculate the average jump time ignoring the first NaN.
    avg_jump = vm_df['jump'].iloc[1:].mean()  # .iloc[1:] skips the first NaN diff
    average_jumps[vm] = avg_jump

# Print out the average jump time per VM.
for vm, avg in average_jumps.items():
    print(f"Average jump time for VM {vm}: {avg}")