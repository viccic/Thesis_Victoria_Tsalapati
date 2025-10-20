import numpy as np
import matplotlib.pyplot as plt


with open("/path/to/your/sensor/data/csv", encoding="utf-8-sig") as f:
    sensor_data = np.loadtxt(f, delimiter=",")

with open("/path/to/your/simulated/data/csv", encoding="utf-8-sig") as f:
    simulation_data = np.loadtxt(f, delimiter=",")

# Errors
errors = sensor_data - simulation_data

# Error statistics
mean_error = np.mean(errors)
rmse = np.sqrt(np.mean(errors**2))

print(f"Mean Bias Error: {mean_error:.2f}")
print(f"RMSE: {rmse:.2f}")

# Histogram with more x-axis ticks
plt.figure(figsize=(10, 6))
counts, bins, patches = plt.hist(errors, bins=50, color='skyblue', edgecolor='black')

# Add counts on bars
for count, bin_left, bin_right in zip(counts, bins[:-1], bins[1:]):
    if count > 0:
        plt.text((bin_left + bin_right) / 2, count, str(int(count)),
                 ha='center', va='bottom', fontsize=7)

# Add vertical line for mean
plt.axvline(mean_error, color='red', linestyle='--', label=f"Mean = {mean_error:.2f}")

plt.xlabel("Error")
plt.ylabel("Frequency")
plt.title(f"Error Distribution Histogram")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(bins, [f"{b:.3f}" for b in bins], rotation=90)
plt.tight_layout()
plt.legend()
filename = "/path/to/save/output/png"
plt.savefig(filename, dpi=300, bbox_inches="tight")
plt.show()
