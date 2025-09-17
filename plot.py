import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# DELAY DATA
df = pd.read_excel("/home/acems/Ali/delay_rep5.xlsx")
df['delay'] = df['scenario'].str.replace('delay_', '').astype(float)
df = df.sort_values('delay')
delays = sorted(df['delay'].unique())
crash_data = [df[df['delay'] == d]['n_crashes'] for d in delays]
ssm_data = [df[df['delay'] == d]['ssm_mean'] for d in delays]
mean_crashes = [np.mean(c) for c in crash_data]
mean_ssm = [np.mean(s) for s in ssm_data]

fig, ax1 = plt.subplots(figsize=(14, 6))
bp1 = ax1.boxplot(
    crash_data, positions=np.arange(len(delays)) - 0.15, widths=0.25,
    patch_artist=True, boxprops=dict(facecolor='skyblue', color='blue', linewidth=2),
    medianprops=dict(color='navy', linewidth=2), whiskerprops=dict(color='blue'),
    capprops=dict(color='blue'), showfliers=False
)
crash_mean_line, = ax1.plot(np.arange(len(delays)) - 0.15, mean_crashes, color='blue', marker='o', linewidth=2, label="Crash Count Mean")
ax1.set_ylabel("Crash Count per Run", color='blue', fontsize=14, weight='normal')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xlabel("Communication Delay (s)", fontsize=14, weight='normal')
ax2 = ax1.twinx()
bp2 = ax2.boxplot(
    ssm_data, positions=np.arange(len(delays)) + 0.15, widths=0.25,
    patch_artist=True, boxprops=dict(facecolor='salmon', color='darkred', linewidth=2),
    medianprops=dict(color='firebrick', linewidth=2), whiskerprops=dict(color='darkred'),
    capprops=dict(color='darkred'), showfliers=False
)
ssm_mean_line, = ax2.plot(np.arange(len(delays)) + 0.15, mean_ssm, color='darkred', marker='s', linewidth=2, label="SSM Mean per Run")
ax2.set_ylabel("SSM Mean (s)", color='darkred', fontsize=14, weight='normal')
ax2.tick_params(axis='y', labelcolor='darkred')
ax1.set_xticks(np.arange(len(delays)))
ax1.set_xticklabels([f"{d:.1f}" for d in delays], fontsize=12, weight='normal')
blue_patch = plt.Line2D([0], [0], color='skyblue', marker='s', linestyle='None', markersize=10, label='Crash Count per Run')
red_patch = plt.Line2D([0], [0], color='salmon', marker='s', linestyle='None', markersize=10, label='SSM Mean per Run')
handles = [blue_patch, crash_mean_line, red_patch, ssm_mean_line]
labels = ["Crash Count per Run", "Crash Count Mean", "SSM Mean per Run", "SSM Mean"]
plt.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.27), ncol=4, fontsize=12, frameon=False)
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.show()

# PACKET LOSS DATA
df_ploss = pd.read_excel("/home/acems/Ali/ploss_rep5.xlsx")
df_ploss['ploss'] = df_ploss['scenario'].str.replace('loss_', '').astype(float)
df_ploss = df_ploss.sort_values('ploss')
plosses = sorted(df_ploss['ploss'].unique())
crash_data_ploss = [df_ploss[df_ploss['ploss'] == p]['n_crashes'] for p in plosses]
ssm_data_ploss = [df_ploss[df_ploss['ploss'] == p]['ssm_mean'] for p in plosses]
mean_crashes_ploss = [np.mean(c) for c in crash_data_ploss]
mean_ssm_ploss = [np.mean(s) for s in ssm_data_ploss]
fig, ax1 = plt.subplots(figsize=(14, 6))
bp1 = ax1.boxplot(
    crash_data_ploss, positions=np.arange(len(plosses)) - 0.15, widths=0.25,
    patch_artist=True, boxprops=dict(facecolor='skyblue', color='blue', linewidth=2),
    medianprops=dict(color='navy', linewidth=2), whiskerprops=dict(color='blue'),
    capprops=dict(color='blue'), showfliers=False
)
crash_mean_line, = ax1.plot(np.arange(len(plosses)) - 0.15, mean_crashes_ploss, color='blue', marker='o', linewidth=2, label="Crash Count Mean")
ax1.set_ylabel("Crash Count per Run", color='blue', fontsize=14, weight='normal')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xlabel("Packet Loss (%)", fontsize=14, weight='normal')
ax2 = ax1.twinx()
bp2 = ax2.boxplot(
    ssm_data_ploss, positions=np.arange(len(plosses)) + 0.15, widths=0.25,
    patch_artist=True, boxprops=dict(facecolor='salmon', color='darkred', linewidth=2),
    medianprops=dict(color='firebrick', linewidth=2), whiskerprops=dict(color='darkred'),
    capprops=dict(color='darkred'), showfliers=False
)
ssm_mean_line, = ax2.plot(np.arange(len(plosses)) + 0.15, mean_ssm_ploss, color='darkred', marker='s', linewidth=2, label="SSM Mean per Run")
ax2.set_ylabel("SSM Mean (s)", color='darkred', fontsize=14, weight='normal')
ax2.tick_params(axis='y', labelcolor='darkred')
ax1.set_xticks(np.arange(len(plosses)))
ax1.set_xticklabels([f"{p:.2f}" for p in plosses], fontsize=12, weight='normal')
blue_patch = plt.Line2D([0], [0], color='skyblue', marker='s', linestyle='None', markersize=10, label='Crash Count per Run')
red_patch = plt.Line2D([0], [0], color='salmon', marker='s', linestyle='None', markersize=10, label='SSM Mean per Run')
handles = [blue_patch, crash_mean_line, red_patch, ssm_mean_line]
labels = ["Crash Count per Run", "Crash Count Mean", "SSM Mean per Run", "SSM Mean"]
plt.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.27), ncol=4, fontsize=12, frameon=False)
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.show()

# DETECTION ERROR DATA
df_error = pd.read_excel("/home/acems/Ali/deterror_rep5.xlsx")
df_error['error'] = df_error['scenario'].str.replace('err_', '').astype(float)
df_error = df_error.sort_values('error')

# Only include errors with at least one run
errors_all = sorted(df_error['error'].unique())
crash_data_error = [df_error[df_error['error'] == e]['n_crashes'] for e in errors_all]
ssm_data_error = [df_error[df_error['error'] == e]['ssm_mean'] for e in errors_all]

# Filter out errors with empty data
filtered_errors = []
filtered_crash_data = []
filtered_ssm_data = []
for e, cdata, sdata in zip(errors_all, crash_data_error, ssm_data_error):
    if len(cdata) > 0 and len(sdata) > 0:
        filtered_errors.append(e)
        filtered_crash_data.append(cdata)
        filtered_ssm_data.append(sdata)

mean_crashes_error = [np.mean(c) for c in filtered_crash_data]
mean_ssm_error = [np.mean(s) for s in filtered_ssm_data]

fig, ax1 = plt.subplots(figsize=(14, 6))
bp1 = ax1.boxplot(
    filtered_crash_data, positions=np.arange(len(filtered_errors)) - 0.15, widths=0.25,
    patch_artist=True, boxprops=dict(facecolor='skyblue', color='blue', linewidth=2),
    medianprops=dict(color='navy', linewidth=2), whiskerprops=dict(color='blue'),
    capprops=dict(color='blue'), showfliers=False
)
crash_mean_line, = ax1.plot(np.arange(len(filtered_errors)) - 0.15, mean_crashes_error, color='blue', marker='o', linewidth=2, label="Crash Count Mean")
ax1.set_ylabel("Crash Count per Run", color='blue', fontsize=14, weight='normal')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xlabel("Detection Error", fontsize=14, weight='normal')
ax2 = ax1.twinx()
bp2 = ax2.boxplot(
    filtered_ssm_data, positions=np.arange(len(filtered_errors)) + 0.15, widths=0.25,
    patch_artist=True, boxprops=dict(facecolor='salmon', color='darkred', linewidth=2),
    medianprops=dict(color='firebrick', linewidth=2), whiskerprops=dict(color='darkred'),
    capprops=dict(color='darkred'), showfliers=False
)
ssm_mean_line, = ax2.plot(np.arange(len(filtered_errors)) + 0.15, mean_ssm_error, color='darkred', marker='s', linewidth=2, label="SSM Mean per Run")
ax2.set_ylabel("SSM Mean (s)", color='darkred', fontsize=14, weight='normal')
ax2.tick_params(axis='y', labelcolor='darkred')
ax1.set_xticks(np.arange(len(filtered_errors)))
ax1.set_xticklabels([f"{e:.1f}" for e in filtered_errors], fontsize=12, weight='normal')
blue_patch = plt.Line2D([0], [0], color='skyblue', marker='s', linestyle='None', markersize=10, label='Crash Count per Run')
red_patch = plt.Line2D([0], [0], color='salmon', marker='s', linestyle='None', markersize=10, label='SSM Mean per Run')
handles = [blue_patch, crash_mean_line, red_patch, ssm_mean_line]
labels = ["Crash Count per Run", "Crash Count Mean", "SSM Mean per Run", "SSM Mean"]
plt.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.27), ncol=4, fontsize=12, frameon=False)
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.show()