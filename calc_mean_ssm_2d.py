import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# ---- All parameters set to zero (ideal conditions) ----
LEADER_LENGTH = 4.5  # meters
LEADER_WIDTH = 1.8   # meters
FOLLOWER_WIDTH = 1.8 # meters
EPS_X_MAX = 0.0      # max distance detection error (meters)
EPS_Y_MAX = 0.0      # max lateral detection error (meters)
EPS_VF_MAX = 0.0     # max speed error follower (m/s)
EPS_VL_MAX = 0.0     # max speed error leader (m/s)
TAU_DELAY = 0.0      # communication delay (seconds)
T_P = 0.1            # packet interarrival time (s)
P_LOSS = 0.0         # packet loss rate (0-1)
SSM_UPPER = 5.0      # screening threshold for SSM (seconds)

def effective_delay(tau_delay, t_p, p_loss):
    if p_loss < 1.0:
        return tau_delay + (p_loss * t_p) / max(1e-6, 1 - p_loss)
    else:
        return 1e6

def parse_fcd(fcd_file):
    traj = []
    for event, elem in ET.iterparse(fcd_file, events=("end",)):
        if elem.tag == "timestep":
            time = float(elem.attrib["time"])
            vehicles = {}
            for v in elem:
                vid = v.attrib["id"]
                x = float(v.attrib["x"])
                y = float(v.attrib["y"])
                speed = float(v.attrib["speed"])
                lane = v.attrib.get("lane", None)
                vehicles[vid] = {"x": x, "y": y, "speed": speed, "lane": lane}
            traj.append({"time": time, "vehicles": vehicles})
            elem.clear()
    return traj

def calculate_ssm_2d(traj,
                     leader_length=4.5,
                     leader_width=1.8,
                     follower_width=1.8,
                     eps_x_max=0.0,
                     eps_y_max=0.0,
                     eps_vf_max=0.0,
                     eps_vl_max=0.0,
                     tau_delay=0.0,
                     t_p=0.1,
                     p_loss=0.0,
                     ssm_upper=5.0):
    ssm_list = []
    eff_delay = effective_delay(tau_delay, t_p, p_loss)
    for step in traj:
        vehicles = step["vehicles"]
        for ego_id, ego in vehicles.items():
            ego_x = ego["x"]
            ego_y = ego["y"]
            ego_speed = ego["speed"]
            ego_lane = ego["lane"]
            # Find leader (same lane, ahead)
            min_dx = float('inf')
            leader_id = None
            for other_id, other in vehicles.items():
                if other_id != ego_id and other["lane"] == ego_lane:
                    dx = other["x"] - ego_x
                    if 0 < dx < min_dx:
                        min_dx = dx
                        leader_id = other_id
            if leader_id:
                leader = vehicles[leader_id]
                leader_x = leader["x"]
                leader_y = leader["y"]
                leader_speed = leader["speed"]
                # --- Compute deltas (no error terms) ---
                delta_x = max(0, (leader_x - leader_length) - ego_x)
                delta_y = max(0, abs(ego_y - leader_y) - (follower_width + leader_width)/2)
                num = np.sqrt(delta_x**2 + delta_y**2) - (ego_speed - leader_speed) * eff_delay
                denom = ego_speed - leader_speed
                if denom > 0:
                    ssm = num / denom
                    if 0 < ssm <= ssm_upper:
                        ssm_list.append(ssm)
    return ssm_list

if __name__ == "__main__":
    fcd_file = "fcd.xml"
    traj = parse_fcd(fcd_file)
    ssm_values = calculate_ssm_2d(
        traj,
        leader_length=LEADER_LENGTH,
        leader_width=LEADER_WIDTH,
        follower_width=FOLLOWER_WIDTH,
        eps_x_max=EPS_X_MAX,
        eps_y_max=EPS_Y_MAX,
        eps_vf_max=EPS_VF_MAX,
        eps_vl_max=EPS_VL_MAX,
        tau_delay=TAU_DELAY,
        t_p=T_P,
        p_loss=P_LOSS,
        ssm_upper=SSM_UPPER
    )
    if ssm_values:
        mean_ssm = np.mean(ssm_values)
    else:
        mean_ssm = float('nan')
    pd.DataFrame([{"mean_ssm_2d": mean_ssm}]).to_csv("mean_ssm_2d.csv", index=False)
    print(f"Mean SSM 2D (ideal, SSM ≤ {SSM_UPPER}s): {mean_ssm:.3f} (saved as mean_ssm_2d.csv)")
