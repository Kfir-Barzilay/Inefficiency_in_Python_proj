# Updating the chart title
import matplotlib.pyplot as plt
import schedule
fig, ax = plt.subplots(figsize=(12, 6))

for task_idx, week_indices in schedule.items():
    for week_idx in week_indices:
        ax.broken_barh([(week_idx * 2, 2)], (task_idx - bar_height / 2, bar_height), facecolors='tab:green')

# Formatting
ax.set_yticks(task_positions)
ax.set_yticklabels(tasks_en, fontsize=9)
ax.set_xticks([i * 2 + 1 for i in range(len(weeks))])
ax.set_xticklabels(weeks, rotation=45)
ax.set_xlim(0, len(weeks) * 2)
ax.set_xlabel("Weeks")
ax.set_title("Characterization of Inefficiency in a Python Interpreter")

plt.tight_layout()
plt.gca().invert_yaxis()
plt.grid(True, axis='x', linestyle='--', alpha=0.7)
plt.box(False)
plt.show()
