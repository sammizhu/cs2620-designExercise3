import pandas as pd
import matplotlib.pyplot as plt
import os

# Read the CSV file; adjust the filename as needed.
csv_filename = "Probability-Trial5.csv"
df = pd.read_csv(csv_filename)

# Convert "Global Time" to datetime (if needed)
df['Global Time'] = pd.to_datetime(df['Global Time'])

# Create boolean columns for each VM based on non-empty cells.
df['VM_ID1'] = df['VM_1'].notnull() & (df['VM_1'].astype(str).str.strip() != "")
df['VM_ID2'] = df['VM_2'].notnull() & (df['VM_2'].astype(str).str.strip() != "")
df['VM_ID3'] = df['VM_3'].notnull() & (df['VM_3'].astype(str).str.strip() != "")

# Filter the data for each VM.
vm1 = df[df['VM_ID1']]
vm2 = df[df['VM_ID2']]
vm3 = df[df['VM_ID3']]

print("VM1 rows:", len(vm1))
print("VM2 rows:", len(vm2))
print("VM3 rows:", len(vm3))

# Create the plot.
plt.figure(figsize=(12, 6))

plt.plot(vm1['Global Time'], vm1['Length of Queue'], marker='o', label="VM1 (Clock Speed = 1)")
plt.plot(vm2['Global Time'], vm2['Length of Queue'], marker='o', label="VM2 (Clock Speed = 1)")
plt.plot(vm3['Global Time'], vm3['Length of Queue'], marker='o', label="VM3 (Clock Speed = 6)")

plt.xlabel("Global Time")
plt.ylabel("Length of Queue")
plt.title("Global Time vs. Length of Queue (by VM)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Save the figure using the same base name as the CSV file.
base_name = os.path.splitext(csv_filename)[0]
output_filename = "images/probability/trial5/" + base_name + ".png"
plt.savefig(output_filename)
print(f"Plot saved as {output_filename}")

plt.show()