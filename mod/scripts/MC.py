from time import sleep
from mod.helpers.constants.definitions import (
    change_types,
    endpoints,
    olt_devices,
    payload,
)
from mod.helpers.handlers.add_onu import add_service
from mod.helpers.handlers.request import db_request
from mod.helpers.utils.ssh import ssh


def client_modify(data):
    change_type = data["modify"]
    message = "success"

    payload_new = payload.copy()
    payload["lookup_type"] = "C"
    payload["lookup_value"] = {"contract": data["contract"], "olt": data["olt"]}
    req = db_request(endpoints["get_client"], payload)
    if req["data"] is None:
        return {
            "message": "The required OLT & ONT does not exists",
            "contract": data["contract"],
        }

    client = req["data"]
    (_, command, quit_ssh) = ssh(olt_devices[str(client["olt"])])

    if change_type not in change_types:
        quit_ssh()
        message = "Modify type does not exist"
        return {"message": message, "error": True, "data": None}

    payload["change_field"] = change_type
    new_values = data["new_values"]

    if change_type == "CT":
        command(f'interface gpon {client["frame"]}/{client["slot"]}')
        command(
            f'ont modify {client["port"]} {client["onu_id"]} desc "{new_values["name_1"]} {new_values["name_2"]} {new_values["contract"]}"'
        )
        client["contract"] = new_values["contract"]

    if change_type == "CP":
        client["device_type"] = new_values["device_type"]
        db_req = db_request(endpoints["get_plans"], {})
        db_plans = db_req["data"]
        plan_lists = [item["plan_name"] for item in db_plans]

        if new_values["plan_name"] not in plan_lists:
            quit_ssh()
            message = "Selected plan does not exist."
            return {"message": message, "error": True, "data": None}

        plan = next(
            (item for item in db_plans if item["plan_name"] == new_values["plan_name"]),
            None,
        )
        command(f'undo service-port {client["spid"]}')
        command(f'interface gpon {client["frame"]}/{client["slot"]}')
        command(
            f"ont modify {client['port']} {client['onu_id']} ont-lineprofile-id {plan['line_profile']}"
        )
        command(
            f"ont modify {client['port']} {client['onu_id']} ont-srvprofile-id {plan['srv_profile']}"
        )
        client["wan"] = [plan]
        client["plan_name"] = new_values["plan_name"]
        client["assigned_ip_address"] = new_values["assigned_ip_address"]
        add_service(command, client)
    if change_type == "CO":
        command(f'interface gpon {client["frame"]}/{client["slot"]}')
        command(f'ont modify {client["port"]} {client["onu_id"]} sn {new_values["sn"]}')

    if change_type == "EC":
        command(f'undo service-port {client["spid"]}')
        command(f'interface gpon {client["frame"]}/{client["slot"]}')
        command(f'ont delete {client["port"]} {client["onu_id"]}')
        sleep(3)
        req = db_request(endpoints["remove_client"], payload)
        if req["error"]:
            message = "an error occurred deleting client from db"
        quit_ssh()
        return {"message": message, "error": False, "data": req["data"]}

    payload["new_values"] = new_values
    req = (
        db_request(endpoints["update_client"], payload)
        if "EC" != change_type
        else db_request(endpoints["remove_client"], payload)
    )
    if req["error"]:
        message = "an error occurred updating client from db"
    quit_ssh()
    payload_new["lookup_type"] = "C"
    payload_new["lookup_value"] = {"contract": client["contract"], "olt": data["olt"]}
    req_new = (
        db_request(endpoints["get_client"], payload_new) if "EC" != change_type else req
    )
    return {"message": message, "error": False, "data": req_new["data"]}
