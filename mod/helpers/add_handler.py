from time import sleep
from mod.helpers.spid import availableSpid, spidCalc
from mod.helpers.decoder import decoder, check
from mod.helpers.fail_handler import failChecker


def add_onu(comm, command, data):
    command(f"interface gpon {data['frame']}/{data['slot']}")
    command(
        f'ont add {data["port"]} sn-auth {data["sn"]} omci ont-lineprofile-id {data["line_profile"]} ont-srvprofile-id {data["srv_profile"]} desc "{data["name"]}" '
    )
    value = decoder(comm)
    fail = failChecker(value)
    if fail == None:
        (_, end) = check(value, "ONTID :").span()
        ID = value[end: end +
                   3].replace(" ", "").replace("\n", "").replace("\r", "")
        command(
            f'ont optical-alarm-profile {data["port"]} {ID} profile-name ALARMAS_OPTICAS'
        )
        command(
            f'ont alarm-policy {data["port"]} {ID} policy-name FAULT_ALARMS'
        )
        command("quit")
        return (ID, fail)
    else:
        return (None, fail)


def add_service(comm, command, data):
    data["wan"][0]["spid"] = spidCalc(data)["I"] if "_IP" not in data["plan_name"] else spidCalc(data)["P"]

    command(f"interface gpon {data['frame']}/{data['slot']}")

    command(f" ont port native-vlan {data['port']} {data['onu_id']} eth 1 vlan {data['wan'][0]['vlan']}") if data["device_type"] == "B" else None

    command(f"ont ipconfig {data['port']} {data['onu_id']} ip-index 2 dhcp vlan {data['wan'][0]['vlan']}") if "_IP" not in data["plan_name"] else command(f"ont ipconfig {data['port']} {data['onu_id']} ip-index 2 static ip-address {data['assigned_public_ip']} mask 255.255.255.128 gateway 181.232.181.129 pri-dns 9.9.9.9 slave-dns 149.112.112.112 vlan 102")

    command(f"ont internet-config {data['port']} {data['onu_id']} ip-index 2")
    
    command(f"ont policy-route-config {data['port']} {data['onu_id']} profile-id 2")

    command("quit")
    command(f"""service-port {data['wan'][0]['spid']} vlan {data['wan'][0]['vlan']} gpon {data['frame']}/{data['slot']}/{data['port']} ont {data['onu_id']} gemport {data["wan"][0]['gem_port']} multi-service user-vlan {data['wan'][0]['vlan']} tag-transform transparent inbound traffic-table index {data["wan"][0]["plan"]} outbound traffic-table index {data["wan"][0]["plan"]}"""
            )

    sleep(10)
    command(f"interface gpon {data['frame']}/{data['slot']}")
    command(f"ont wan-config {data['port']} {data['onu_id']} ip-index 2 profile-id 0")
    command("quit")
