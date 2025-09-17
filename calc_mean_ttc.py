import xml.etree.ElementTree as ET
import pandas as pd

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

def calculate_ttc(traj, ttc_upper=5):
    ttc_list = []
    for step in traj:
        vehicles = step["vehicles"]
        for ego_id, ego in vehicles.items():
            ego_x = ego["x"]
            ego_lane = ego["lane"]
            min_dx = float('inf')
            leader_id = None
            for other_id, other in vehicles.items():
                if other_id != ego_id and other["lane"] == ego_lane:
                    dx = other["x"] - ego_x
                    if 0 < dx < min_dx:
                        min_dx = dx
                        leader_id = other_id
            if leader_id:
                ego_speed = ego["speed"]
                leader_speed = vehicles[leader_id]["speed"]
                rel_speed = ego_speed - leader_speed
                if rel_speed > 0:
                    ttc = min_dx / rel_speed
                    if ttc <= ttc_upper:  # Only keep TTC <= 5 s
                        ttc_list.append(ttc)
    return ttc_list

if __name__ == "__main__":
    fcd_file = "fcd.xml"
    traj = parse_fcd(fcd_file)
    ttc_values = calculate_ttc(traj, ttc_upper=5)
    
    if ttc_values:
        mean_ttc = sum(ttc_values) / len(ttc_values)
    else:
        mean_ttc = float('nan')
    
    # Save to CSV
    df = pd.DataFrame([{"mean_ttc": mean_ttc}])
    df.to_csv("mean_ttc.csv", index=False)
    
    print(f"Mean TTC (TTC ≤ 5s): {mean_ttc:.2f} s (saved as mean_ttc.csv)")
