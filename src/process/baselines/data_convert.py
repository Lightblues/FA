""" 
--- input ---
# STAR dataset (24 tasks)
/work/huabu/data/STAR/tasks_transfered
├── code
├── CoRE
├── flowchart
├── NL
├── PDL
└── pseudo
/work/huabu/data/STAR/user_profile
├── apartment_schedule.json
├── apartment_search.json
├── bank_balance.json
├── bank_fraud_report.json
├── doctor_followup.json
├── doctor_schedule.json
├── hotel_book.json
├── hotel_search.json
├── hotel_service_request.json
├── meeting_schedule.json
├── party_plan.json
├── party_rsvp.json
├── plane_book.json
├── plane_search.json
├── restaurant_book.json
├── restaurant_search.json
├── ride_book.json
├── ride_change.json
├── ride_status.json
├── spaceship_access_codes.json
├── spaceship_life_support.json
├── trip_directions.json
├── trivia.json
└── weather.json

--- output --- 
/work/huabu/dataset/flowbench
├── code
│   └── 000.py
├── flowchart
│   └── 000.md
├── task_infos.json
├── text
│   └── 000.txt
├── tools
│   └── 000.yaml
└── user_profiles
    └── 000.json
# task_infos.json
{
    "000":{
        "name": "flight booking",
        "task_background": "flight booking"
    }
}
"""
# %%
import os, sys, json, yaml, pathlib

# IDIR = pathlib.Path("/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/data/STAR/tasks_transfered")
# ODIR = pathlib.Path("/work/huabu/dataset/STAR")
IDIR = pathlib.Path("/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/data/SGD/workflows")
ODIR = pathlib.Path("/work/huabu/dataset/SGD")
os.makedirs(ODIR, exist_ok=True)

def build_name_map(subdir="../user_profile"):
    fns = os.listdir(IDIR / subdir)
    fns.sort()
    # remove the extension
    names = [os.path.splitext(fn)[0] for fn in fns]
    _map = {name: f"{i:03d}" for i, name in enumerate(names)}
    return _map
name_map = build_name_map()

def check_is_binary(fn):
    with open(fn, "rb") as f:
        code = f.read()
    return b'\0' in code


# %%
def build_task_infos(version="v240908"):
    print(f"Converting task infos from `NL` subfolder")
    task_infos = {}
    for name in name_map:
        try: 
            if check_is_binary(IDIR / "NL" / f"{name}.json"):
                raise Exception(f"{name} is binary")
            with open(IDIR / "NL" / f"{name}.json", "r") as f:
                infos = json.load(f)
            task_infos[name_map[name]] = {
                "name": infos["task_name"],
                "task_background": infos["task_description"],
            }
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    result = {
        "version": version,
        "task_infos": task_infos
    }
    print(f"Converted {len(task_infos)} tasks")
    with open(ODIR / "task_infos.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return task_infos
task_infos = build_task_infos()

# %%
def convert_format_code():
    print(f"Converting code from `code` subfolder")
    os.makedirs(ODIR / "code", exist_ok=True)
    num_success = 0
    for name in name_map:
        try:
            # check that code in not binary
            if check_is_binary(IDIR / "code" / f"{name}.py"):
                raise Exception(f"{name} is binary")
            with open(IDIR / "code" / f"{name}.py", "r") as f:
                code = f.read()
            with open(ODIR / "code" / f"{name_map[name]}.py", "w") as f:
                f.write(code)
            num_success += 1
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    print(f"Converted {num_success} tasks")
convert_format_code()

# %%
def convert_format_flowchart():
    print(f"Converting flowchart from `flowchart` subfolder")
    os.makedirs(ODIR / "flowchart", exist_ok=True)
    num_success = 0
    for name in name_map:
        try:
            # check that code in not binary
            if check_is_binary(IDIR / "flowchart" / f"{name}.txt"):
                raise Exception(f"{name} is binary")
            with open(IDIR / "flowchart" / f"{name}.txt", "r") as f:
                flowchart = f.read()
            with open(ODIR / "flowchart" / f"{name_map[name]}.md", "w") as f:
                f.write(flowchart)
            num_success += 1
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    print(f"Converted {num_success} tasks")
    return num_success
convert_format_flowchart()

# %%
def convert_format_text():
    print(f"Converting text from `NL` subfolder")
    os.makedirs(ODIR / "text", exist_ok=True)
    num_success = 0
    for name in name_map:
        try:
            # check that code in not binary
            if check_is_binary(IDIR / "NL" / f"{name}.json"):
                raise Exception(f"{name} is binary")
            with open(IDIR / "NL" / f"{name}.json", "r") as f:
                data = json.load(f)
            with open(ODIR / "text" / f"{name_map[name]}.txt", "w") as f:
                f.write(data["task_detailed_description"])
            num_success += 1
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    print(f"Converted {num_success} tasks")
    return num_success
convert_format_text()

# %%
def fix_typo(d: dict, old_key: str = "interative_pattern", new_key: str = "interactive_pattern"):
    # interative_pattern -> interactive_pattern
    if old_key in d:
        d[new_key] = d[old_key]
        del d[old_key]
    return d

def convert_format_userprofile():
    print(f"Converting user profile from `../user_profile` subfolder")
    os.makedirs(ODIR / "user_profile", exist_ok=True)
    num_success = 0
    for name in name_map:
        try:
            # check that code in not binary
            if check_is_binary(IDIR / "../user_profile" / f"{name}.json"):
                raise Exception(f"{name} is binary")
            with open(IDIR / "../user_profile" / f"{name}.json", "r") as f:
                data = json.load(f)
            data = [fix_typo(d) for d in data]
            with open(ODIR / "user_profile" / f"{name_map[name]}.json", "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            num_success += 1
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    print(f"Converted {num_success} tasks")
    return num_success
convert_format_userprofile()

# %%
def convert_format_api(subdir="../apis/apis_transfered"):
    print(f"Converting api from `{subdir}` subfolder")
    os.makedirs(ODIR / "tools", exist_ok=True)
    num_success = 0
    for name in name_map:
        try:
            # check that code in not binary
            if check_is_binary(IDIR / subdir / f"{name}.json"):
                raise Exception(f"{name} is binary")
            with open(IDIR / subdir / f"{name}.json", "r") as f:
                data = json.load(f)
            with open(ODIR / "tools" / f"{name_map[name]}.yaml", "w") as f:
                yaml.dump(data, f, indent=2)
            num_success += 1
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    print(f"Converted {num_success} tasks")
    return num_success
convert_format_api("../apis")

# %%
