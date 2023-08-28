import matplotlib.pyplot as plt
import numpy as np

singular = np.array([[7.5, 32.3], [14.3, 35.4], [21.8, 32.3], [36.7, 43.3], [72.0, 57.3]])
t_02 = np.array([[10.5, 36.0], [13.3, 37.2], [14.5, 37.8], [16.1, 37.8]])
t_07 = np.array([[10.6, 34.8], [12.7, 37.8], [15.7, 37.2]])

# Plotting
plt.plot(singular[:, 0], singular[:, 1], '-o', color='red', label='Singular')
plt.plot(t_02[:, 0], t_02[:, 1], '-o', color='blue', label='t_0.2')
plt.plot(t_07[:, 0], t_07[:, 1], '-o', color='green', label='t_0.7')

# Adding labels and legend
plt.xlabel('X-Axis')
plt.ylabel('Y-Axis')
plt.title('Comparison of Singular, t_0.2, and t_0.7')
plt.legend()

# Display the plot
plt.show()
