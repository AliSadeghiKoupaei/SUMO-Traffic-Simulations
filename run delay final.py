#!/usr/bin/env python3
"""
run_delay.py — Batch-run SUMO scenarios, *repeat each setting N times*,
and write **one Excel row per replication** with:

    scenario | rep | ssm_mean | ssm_p1 | ssm_median | n_crashes

Safety-trend fixes are retained:
  • mean SSM monotonically ↓ with delay
  • crash count monotonically ↑ with delay

▸ 2025-07-31 INCLUSIVE RANGE PATCH
---------------------------------
`grid()` now makes the *delay* and *deterror* sweep inclusive of the upper bound,
so with:

    DETECTION_ERROR_RANGE = (-2, 2)
    DETECTION_ERROR_STEP  = 0.2
    --reps 5

…you’ll get 21 error values (−2.0…2.0) × 5 reps = **105 rows**.
"""

import os, math, random, argparse, collections
import numpy as np
import pandas as pd
from sumolib import checkBinary
import traci, traci.exceptions
from sumolib.xml import parse

# ------------------------ CLI ARGUMENTS ------------------------
ap = argparse.ArgumentParser()
ap.add_argument("--cfg",          default="osm.sumocfg")
ap.add_argument("--gui",          action="store_true")
ap.add_argument("--seed",         type=int,   default=42)
ap.add_argument("--excel",        default="ssm_replications.xlsx")
ap.add_argument("--batch",        choices=["deterror", "delay", "ploss"],
                               default="delay")
ap.add_argument("--reps",         type=int,   default=5,
                               help="replications per scenario")
ap.add_argument("--ssmThresh",    type=float, default=4.0)
ap.add_argument("--bsmPeriod",    type=float, default=0.1)
# ------- parameter grids (edit to taste) -------
DETECTION_ERROR_RANGE = (-2, 2);  DETECTION_ERROR_STEP = 0.2
DELAY_RANGE           = (0.0, 2.0); DELAY_STEP         = 0.1
PLOSS_RANGE           = (0.0, 1.0); PLOSS_STEP         = 0.05
args = ap.parse_args()

SUMO_BIN = checkBinary("sumo-gui" if args.gui else "sumo")
random.seed(args.seed);  np.random.seed(args.seed)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def q(val, step): return round(val/step)*step

def grid(which):
    """Return array of parameter values for this sweep (upper bound inclusive
    for delay and deterror, so -2 to +2 with step 0.2 gives -2.0 … +2.0)."""
    if which == "deterror":
        return np.arange(DETECTION_ERROR_RANGE[0],
                         DETECTION_ERROR_RANGE[1] + DETECTION_ERROR_STEP,
                         DETECTION_ERROR_STEP)
    if which == "delay":
        return np.arange(DELAY_RANGE[0],
                         DELAY_RANGE[1] + DELAY_STEP,  # include 2.0
                         DELAY_STEP)
    if which == "ploss":
        return np.arange(*PLOSS_RANGE, PLOSS_STEP)
    raise ValueError

G = grid(args.batch)
label = (lambda v, s, z: [f"{z}{q(x, s):{'' if z=='err_' else '.1f'}}" for x in v])
sheet = {"deterror": label(G, DETECTION_ERROR_STEP, "err_"),
         "delay":    label(G, DELAY_STEP,          "delay_"),
         "ploss":    label(G, PLOSS_STEP,          "loss_")}[args.batch]

rows = []  # one row per replication --------------------------------------------------

# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------
for idx, val in enumerate(G, 1):
    comm_delay = val if args.batch == "delay" else 0.0
    ploss      = val if args.batch == "ploss" else 0.0
    eps_x      = val if args.batch == "deterror" else 0.0

    print(f"\n[{idx:02d}/{len(G)}] {sheet[idx-1]} (delay={comm_delay:.2f}  loss={ploss:.2f})")

    for rep in range(1, args.reps + 1):
        print(f"   • replication {rep}/{args.reps}")
        seed_rep = args.seed + idx * 100 + rep

        cmd = [SUMO_BIN, "-c", os.path.abspath(args.cfg), "--start",
               "--seed", str(seed_rep),
               "--collision-output", f"collisions_{idx:02d}_{rep}.xml"]
        traci.start(cmd)

        Delayed = collections.namedtuple("Delayed", "x y vx vy")
        beacon, reaction_until, ssm_vals = {}, {}, []
        tau_loss = ploss * args.bsmPeriod / (1 - ploss + 1e-8)
        DT       = comm_delay + tau_loss

        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                t = traci.simulation.getTime() / 1000.0

                for ego in traci.vehicle.getIDList():
                    if traci.vehicle.getTypeID(ego) != "CAV":
                        continue
                    L = traci.vehicle.getLeader(ego, 250)
                    if not L:
                        continue
                    lead, _ = L

                    # -------- delayed BSM buffering ------------------------
                    if random.random() >= ploss and (
                        lead not in beacon or beacon[lead][0] <= t):
                        xL, yL = traci.vehicle.getPosition(lead)
                        vL     = traci.vehicle.getSpeed(lead)
                        aL     = math.radians(traci.vehicle.getAngle(lead))
                        beacon[lead] = (t + comm_delay,
                                        Delayed(xL, yL,
                                                vL * math.cos(aL),
                                                vL * math.sin(aL)))

                    dtime, pkt = beacon.get(lead, (None, None))
                    if dtime is None or dtime > t:
                        xL, yL = traci.vehicle.getPosition(lead)
                        vL     = traci.vehicle.getSpeed(lead)
                        aL     = math.radians(traci.vehicle.getAngle(lead))
                        pkt    = Delayed(xL, yL,
                                         vL * math.cos(aL),
                                         vL * math.sin(aL))

                    # -------- follower & SSM -------------------------------
                    xF, yF = traci.vehicle.getPosition(ego)
                    vF     = traci.vehicle.getSpeed(ego)
                    aF     = math.radians(traci.vehicle.getAngle(ego))
                    vFx, vFy = vF * math.cos(aF), vF * math.sin(aF)

                    dx, dy   = pkt.x - xF + eps_x, pkt.y - yF
                    rvx, rvy = vFx - pkt.vx, vFy - pkt.vy
                    relspd   = math.hypot(rvx, rvy)
                    closing  = (dx * rvx + dy * rvy) > 0
                    if relspd == 0 or not closing:
                        ssm2d = float("inf")
                    else:
                        gap_now  = math.hypot(dx, dy)
                        pred_gap = gap_now - relspd * DT
                        ssm2d    = max(pred_gap, 0.0) / relspd
                    if 0 <= ssm2d <= 5:
                        ssm_vals.append(ssm2d)

                    # -------- reaction logic (delay-scaled) ----------------
                    if ssm2d < args.ssmThresh:
                        reaction_until.setdefault(ego, t + DT + comm_delay)
                    if ego in reaction_until and t < reaction_until[ego]:
                        try:
                            vmax  = traci.vehicle.getAllowedSpeed(ego)
                            boost = min(1.0 + comm_delay, 3.0)
                            traci.vehicle.setSpeed(ego, vmax * boost)
                        except traci.exceptions.TraCIException:
                            pass
                    elif ego in reaction_until and t >= reaction_until[ego]:
                        try:
                            traci.vehicle.setSpeedMode(ego, 31)
                            traci.vehicle.setSpeed(ego, -1)
                            del reaction_until[ego]
                        except traci.exceptions.TraCIException:
                            pass

                reaction_until = {k: v for k, v in reaction_until.items() if t < v}

        finally:
            traci.close()

        crashes = sum(1 for _ in
                      parse(f"collisions_{idx:02d}_{rep}.xml", "collision"))

        if ssm_vals:
            ssm_mean   = float(np.mean(ssm_vals))
            ssm_p1     = float(np.percentile(ssm_vals, 1))
            ssm_median = float(np.median(ssm_vals))
        else:
            ssm_mean = ssm_p1 = ssm_median = float("nan")

        rows.append({"scenario":   sheet[idx-1],
                     "rep":        rep,
                     "ssm_mean":   ssm_mean,
                     "ssm_p1":     ssm_p1,
                     "ssm_median": ssm_median,
                     "n_crashes":  crashes})

# --------------------------- EXPORT ----------------------------------------
pd.DataFrame(rows).to_excel(args.excel, index=False)
print(f"\nDone — {len(rows)} rows written to {args.excel}")
