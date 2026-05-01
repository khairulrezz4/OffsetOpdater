import os
import json
import requests

# Raw GitHub URLs (more reliable)
urls = {
    "info": "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/info.json",
    "offsets": "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json",
    "client_dll": "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json",
}

def get_build_number():
    try:
        response = requests.get(urls["info"])
        if response.status_code == 200:
            data = response.json()
            return int(data.get("build_number", 0))
    except:
        pass
    return 0


def get_json(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


def get_field(classes, class_name, field_name, fallback=None):
    class_data = classes.get(class_name, {})
    fields = class_data.get("fields", {})
    return fields.get(field_name, fallback)


def find_offsets_file():
    if os.path.isfile("offsets/offsets.json"):
        return "offsets/offsets.json"
    if os.path.isfile("offsets.json"):
        return "offsets.json"
    return None


dest_path = find_offsets_file()

if not dest_path:
    print("offsets.json not found. Creating new one.")
    dest_path = "offsets.json"
    with open(dest_path, "w") as f:
        json.dump({}, f)


build_number = get_build_number()

if build_number == 0:
    print("Failed to get CS2 build number.")
    exit(1)


offsets_remote = get_json(urls["offsets"])
client_remote = get_json(urls["client_dll"])

if not offsets_remote or not client_remote:
    print("Failed to download latest offsets.")
    exit(1)


with open(dest_path, "r") as f:
    offsets_local = json.load(f)


current_build = offsets_local.get("build_number", 0)
offsets_before = dict(offsets_local)

print(f"Current build: {current_build} | Latest build: {build_number}")


try:
    # Update build
    offsets_local["build_number"] = build_number

    # Core offsets
    offsets_local["dwBuildNumber"] = offsets_remote["engine2.dll"]["dwBuildNumber"]
    offsets_local["dwLocalPlayer"] = offsets_remote["client.dll"]["dwLocalPlayerPawn"]
    offsets_local["dwLocalPlayerPawn"] = offsets_remote["client.dll"]["dwLocalPlayerPawn"]
    offsets_local["dwLocalPlayerController"] = offsets_remote["client.dll"]["dwLocalPlayerController"]
    offsets_local["dwEntityList"] = offsets_remote["client.dll"]["dwEntityList"]
    offsets_local["dwViewMatrix"] = offsets_remote["client.dll"]["dwViewMatrix"]
    offsets_local["dwPlantedC4"] = offsets_remote["client.dll"]["dwPlantedC4"]

except KeyError as e:
    print("Offset structure changed:", e)
    exit(1)


try:
    classes = client_remote["client.dll"]["classes"]

    # Player pawn
    offsets_local["m_bIsDefusing"] = classes["C_CSPlayerPawn"]["fields"]["m_bIsDefusing"]
    offsets_local["m_ArmorValue"] = classes["C_CSPlayerPawn"]["fields"]["m_ArmorValue"]
    m_p_clipping_weapon = get_field(classes, "C_CSPlayerPawn", "m_pClippingWeapon", offsets_local.get("m_pClippingWeapon"))
    if m_p_clipping_weapon is not None:
        offsets_local["m_pClippingWeapon"] = m_p_clipping_weapon

    # Flash
    offsets_local["m_flFlashOverlayAlpha"] = classes["C_CSPlayerPawnBase"]["fields"]["m_flFlashOverlayAlpha"]

    # Bomb
    offsets_local["m_flC4Blow"] = classes["C_PlantedC4"]["fields"]["m_flC4Blow"]
    offsets_local["m_flNextBeep"] = classes["C_PlantedC4"]["fields"]["m_flNextBeep"]
    offsets_local["m_flTimerLength"] = classes["C_PlantedC4"]["fields"]["m_flTimerLength"]

    # Player controller
    offsets_local["m_hPlayerPawn"] = classes["CCSPlayerController"]["fields"]["m_hPlayerPawn"]
    offsets_local["m_sSanitizedPlayerName"] = classes["CCSPlayerController"]["fields"]["m_sSanitizedPlayerName"]

    # Entity
    offsets_local["m_iHealth"] = classes["C_BaseEntity"]["fields"]["m_iHealth"]
    offsets_local["m_iTeamNum"] = classes["C_BaseEntity"]["fields"]["m_iTeamNum"]
    offsets_local["m_pGameSceneNode"] = classes["C_BaseEntity"]["fields"]["m_pGameSceneNode"]

    # Positions
    offsets_local["m_vOldOrigin"] = classes["C_BasePlayerPawn"]["fields"]["m_vOldOrigin"]
    offsets_local["m_vecAbsOrigin"] = classes["CGameSceneNode"]["fields"]["m_vecAbsOrigin"]

except KeyError as e:
    print("Client schema structure changed:", e)
    exit(1)


if offsets_local == offsets_before:
    print("Offsets already up to date.")
    exit(0)


with open(dest_path, "w") as f:
    json.dump(offsets_local, f, indent=4)


print("Offsets successfully updated.")