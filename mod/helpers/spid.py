from time import sleep
from mod.helpers.decoder import decoder, check, checkIter
from mod.helpers.fail_handler import failChecker
from mod.helpers.file_handler import dataToDict

conditionSpidOnt = "CTRL_C to break"
condition = "-----------------------------------------------------------------------------"
spidHeader = "SPID,ID,ATT,PORT_TYPE,F/S,/P,VPI,VCI,FLOW_TYPE,FLOW_PARA,RX,TX,STATE,"
spidHeader10 = ",SPID,ID,ATT,PORT_TYPE,F/S/P,VPI,VCI,FLOW_TYPE,FLOW_PARA,RX,TX,STATE,"
conditionSPID = """Next valid free service virtual port ID: """
spidCheck = {
    "index": "Index               : ",
    "id": "VLAN ID             : ",
    "attr": "VLAN attr           : ",
    "endAttr": "Port type",
    "plan": "Outbound table name : ",
    "adminStatus": "Admin status        : ",
    "status": "State               : ",
    "endStatus": "Label               :",
}


def ontSpid(comm, command, client):
    command(
        f"display service-port port {client['frame']}/{client['slot']}/{client['port']} ont {client['onu_id']}  |  no-more")
    sleep(2)
    value = decoder(comm)
    fail = failChecker(value)
    if fail == None:
        limits = checkIter(value, condition)
        (_, s) = limits[1]
        (e, _) = limits[2]
        data = dataToDict(spidHeader, value[s: e - 2]) if int(client['slot']) < 10 else dataToDict(spidHeader10, value[s: e - 2])
        return (data, None)
    else:
        return (None, fail)


def availableSpid(comm, command):
    command("display service-port next-free-index")
    command("")
    value = decoder(comm)
    (_, e) = check(value, conditionSPID).span()
    spid = value[e: e + 5].replace(" ", "").replace("\n", "")
    return spid


def spidCalc(data):
    SPID = 12288*(int(data["slot"]) - 1) + 771 * \
        int(data["port"]) + 3 * int(data["onu_id"])
    return {
        "I": SPID,
        "P": SPID + 1,
        "V": SPID + 2
    }
