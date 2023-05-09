from mod.helpers.data_lookup import data_lookup
from mod.scripts.ssh import ssh
from mod.helpers.decoder import decoder
from mod.helpers.wan_lookup import wan
from mod.helpers.add_handler import add_onu, add_service
from mod.helpers.plans import PLANS
from mod.helpers.devices import devices


# def addTest(comm,command):
#   command("interface gpon 0/1")
#   command('ont add 3 sn-auth 4857544329765DA4 omci ont-lineprofile-id 3 ont-srvprofile-id 210 desc "PRUEBA RICK 9999999999"')
#   command("ont optical-alarm-profile 3 0 profile-name ALARMAS_OPTICAS")
#   command("ont alarm-policy 3 0 policy-name FAULT_ALARMS")
#   command("quit")
#   command("interface gpon 0/1")
#   command("ont ipconfig 3 0 ip-index 2 dhcp vlan 3100")
#   command("ont internet-config 3 0 ip-index 2")
#   command("ont policy-route-config 3 0 profile-id 2")
#   command("quit")
#   command("service-port 2313 vlan 3100 gpon 0/1/3 ont 0 gemport 20 multi-service user-vlan 3100 tag-transform transparent inbound traffic-table index 210 outbound traffic-table index 210")
#   command("interface gpon 0/1")
#   command("ont wan-config 3 0 ip-index 2 profile-id 0")
#   command("quit")


def modifyClient(action, data, new_values):
  """
  comm        :   ssh connection handler [class]
  command     :   sends ssh commands [func]
  quit        :   terminates the ssh connection [func]
  olt         :   defines the selected olt [var:str]
  action      :   defines the type of lookup/action of the client [var:str]
  
  This module modifies the data of a given client

  action types:
  
  > (N&C)     :   Modifies Name and contract of client
  > (FSP)     :   Modifies Frame/Slot/Port of client
  > (OSN)     :   Modifies ONU SN of client
  > (DTP)     :   Modifies Device type of client
  > (P&P)     :   Modifies Plan and provider of client
  
  """
  oltOptions = ["1", "2", "3"]
  if data['olt'] in oltOptions:
      ip = devices[f"OLT{data['olt']}"]
      (comm, command, quit) = ssh(ip)
      decoder(comm)
      client,fail = data_lookup(comm,command,data['contract']).values()
      
      if fail == None and client != None:
          client["olt"] = data["olt"]
          if action == "N&C":
            command(f'interface gpon {client["frame"]}/{client["slot"]}')
            command(f'ont modify {client["port"]} {client["onu_id"]} desc "{new_values["name_1"]} {new_values["name_2"]} {new_values["contract"]}" ')
            quit()
            return {
              "error": False,
              "message": "success",
              "client":client
            }
          
          if action == "FSP":
            # ont deletion
            (_,client["wan"]) = wan(comm,command,client)
            for wanData in client["wan"]:
                command(f"undo service-port {wanData['spid']}")
            command(f"interface gpon {client['frame']}/{client['slot']}")
            command(f"ont delete {client['port']} {client['onu_id']} ")
            
            # ont re register
            data = client.copy()
            data['frame'] = new_values['frame']
            data['slot'] = new_values['slot']
            data['port'] = new_values['port']
            data['plan_name'] = client["wan"][0]["plan_name"]
            data["wan"][0] = PLANS[data['plan_name']]
            data['line_profile'] = PLANS[data['plan_name']]["line_profile"]
            data['srv_profile'] = PLANS[data['plan_name']]["srv_profile"]
            data["device_type"] = new_values["device_type"]
            (data['onu_id'], fail_fsp) = add_onu(comm,command,data)
            
            if fail_fsp != None:
              return {
              "error": True,
              "message": fail_fsp,
              "client":data
            }
            
            add_service(comm, command, data)
            quit()
            return {
              "error": False,
              "message": "success",
              "client":data
            }
          
          if action == "OSN":
            (_,client["wan"]) = wan(comm,command,client)
            command(f'interface gpon {client["frame"]}/{client["slot"]}')
            command(f'ont modify {client["port"]} {client["onu_id"]} sn {new_values["sn"]}')
            command(f" ont port native-vlan {client['port']} {client['onu_id']} eth 1 vlan {client['wan'][0]['vlan']}") if new_values["device_type"] == "B" else None
            quit()
            return {
              "error": False,
              "message": "success",
              "client": client
            }
          
          if action == "P&P":
            (_,client["wan"]) = wan(comm,command,client)
            for wanData in client["wan"]:
                command(f"undo service-port {wanData['spid']}")
            command(f"interface gpon {client['frame']}/{client['slot']}")
            client["plan_name"] = new_values["plan_name"]
            client["device_type"] = new_values["device_type"]
            client["wan"][0] = PLANS[new_values["plan_name"]]
            client["assigned_public_ip"] = new_values["assigned_public_ip"] if "_IP" in new_values["plan_name"] else None
            command(f"ont modify {client['port']} {client['onu_id']} ont-lineprofile-id {client['wan'][0]['line_profile']}")
            command(f"ont modify {client['port']} {client['onu_id']} ont-srvprofile-id {client['wan'][0]['srv_profile']}")
            command("quit")
            add_service(comm, command, client)
            quit()
            return {
              "error": False,
              "message": "success",
              "client": client
            }
          
      else:
            return {
              "error": True,
              "message": fail,
              "client":{}
            }