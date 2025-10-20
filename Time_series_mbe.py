import csv
import io
import numpy as np
import matplotlib.pyplot as plt

def error_st_dev(mean_error_array, std_error_array, sensor_path, simulation_path, hours):
    for hour in hours:
        sensor_values = []
        simulation_values = []

        with open(sensor_path, 'rb') as rawfile:
            text_stream = io.TextIOWrapper(rawfile, encoding='utf-8')
            sv_reader = csv.reader(text_stream, delimiter=',', quoting=csv.QUOTE_NONE)

            for row in sv_reader:
                date_str, time_str = row[0].split("T")
                hour_utc = int(time_str.split(":")[0])
                if hour_utc == hour:
                    sensor_values.append(float(row[1]))

        sensor_values= np.array(sensor_values, dtype=float)

        with open(simulation_path, 'rb') as rawfile:
            text_stream = io.TextIOWrapper(rawfile, encoding='utf-8')
            sv_reader = csv.reader(text_stream, delimiter=',', quoting=csv.QUOTE_NONE)
            next(sv_reader)  # skip header row

            for row in sv_reader:
                date_str, time_str = row[0].split("T")
                hour_utc = int(time_str.split(":")[0])
                if hour_utc == hour:
                    simulation_values.append(float(row[1]))

        simulation_values = np.array(simulation_values, dtype=float)

        # Errors
        errors = sensor_values - simulation_values

        # Error statistics
        mean_error = np.mean(errors)
        std_error = np.std(errors)

        mean_error_array.append(mean_error)
        std_error_array.append(std_error)

    return mean_error_array, std_error_array

def diagrams(mean_error_array_clear_sky, std_error_array_clear_sky, mean_error_array_cloudy, std_error_array_cloudy, mean_error_array_intermediate, std_error_array_intermediate, hours_input):
    hours = np.arange(hours_input)

    x = np.arange(len(hours))
    w = 0.25  # bar width

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axhline(0, color='black', linewidth=1)
    ax.set_axisbelow(True)
    ax.grid(True, which='both', axis='both', linestyle='--', alpha=0.6)

    # Three bars per timestamp with their std
    ax.bar(x - w, mean_error_array_clear_sky, w, yerr=std_error_array_clear_sky,
           capsize=4, edgecolor="black", label="Clear Sky")
    ax.bar(x, mean_error_array_intermediate, w, yerr=std_error_array_intermediate,
           capsize=4, edgecolor="black", label="Intermediate")
    ax.bar(x + w, mean_error_array_cloudy, w, yerr=std_error_array_cloudy,
           capsize=4, edgecolor="black", label="Cloudy")

    # Formatting
    ax.set_xticks(x)
    ax.set_xticklabels([f"{h}:00" for h in hours], rotation=60)
    ax.set_xlabel("Hour in UTC")
    ax.set_ylabel("Mean Biased Error (lux)")
    ax.set_title("Mean Biased Error per hour for every sky condition")
    ax.legend()
    filename = "/path/to/save/output/png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.tight_layout()
    plt.show()
    print("mean_error_array_clear_sky:", np.round(mean_error_array_clear_sky,2))
    print("mean_error_array_cloudy:", np.round(mean_error_array_cloudy,2))
    print("mean_error_array_intermediate:", np.round(mean_error_array_intermediate,2))

range_of_hours = "insert the range of hours you wish to include in the time series"

sensor_path_clear_sky = "/path/to/csv/clear_sky/sensor/data"
simulation_path_clear_sky = "/path/to/csv/clear_sky/simulation/data"

sensor_path_cloudy = "/path/to/csv/cloudy/sensor/data"
simulation_path_cloudy = "/path/to/csv/cloudy/simulation/data"

sensor_path_intermediate = "/path/to/csv/intermediate/sensor/data"
simulation_path_intermediate = "/path/to/csv/cloudy/simulation/data"

# Clear sky conditions
mean_error_array_clear_sky = []
std_error_array_clear_sky = []

# Cloudy sky conditions
mean_error_array_cloudy = []
std_error_array_cloudy = []

# Intermediate sky conditions
mean_error_array_intermediate = []
std_error_array_intermediate = []

# Error and st. deviation calculation
mean_error_array_clear_sky, std_error_array_clear_sky = error_st_dev(mean_error_array_clear_sky, std_error_array_clear_sky, sensor_path_clear_sky, simulation_path_clear_sky, range_of_hours)
mean_error_array_cloudy, std_error_array_cloudy = error_st_dev(mean_error_array_cloudy, std_error_array_cloudy, sensor_path_cloudy, simulation_path_cloudy, range_of_hours)
mean_error_array_intermediate, std_error_array_intermediate = error_st_dev(mean_error_array_intermediate, std_error_array_intermediate, sensor_path_intermediate, simulation_path_intermediate, range_of_hours)


# Diagrams
diagrams(mean_error_array_clear_sky, std_error_array_clear_sky, mean_error_array_cloudy, std_error_array_cloudy, mean_error_array_intermediate, std_error_array_intermediate, range_of_hours)



