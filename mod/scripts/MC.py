from mod.helpers.data_lookup import data_lookup
from mod.scripts.ssh import ssh
from mod.helpers.decoder import decoder
from mod.helpers.wan_lookup import wan
from mod.helpers.add_handler import add_onu, add_service
from mod.helpers.plans import PLANS


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
      if client["fail"] == None:
        
          if action == "N&C":
            command(f'interface gpon {client["frame"]}/{client["slot"]}')
            command(f'ont modify {client["port"]} {client["onu_id"]} desc "{new_values["name_1"]} {new_values["name_2"]} {new_values["contract"]}" ')
            return "success message {}"
          
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
            (data['onu_id'], data['fail']) = add_onu(comm,command,data)
            
            if data['fail'] != None:
              return "send error message"
            
            add_service(comm, command, data)
            return "success message {}"
          
          if action == "OSN":
            (_,client["wan"]) = wan(comm,command,client)
            command(f'interface gpon {client["frame"]}/{client["slot"]}')
            command(f'ont modify {client["port"]} {client["onu_id"]} sn {new_values["sn"]}')
            command(f" ont port native-vlan {client['port']} {client['onu_id']} eth 1 vlan {client['wan'][0]['vlan']}") if new_values["device_type"] == "B" else None
            return "success message {}"
          
          if action == "P&P":
            (_,client["wan"]) = wan(comm,command,client)
            for wanData in client["wan"]:
                command(f"undo service-port {wanData['spid']}")
            command(f"interface gpon {client['frame']}/{client['slot']}")
            client["wan"][0] = PLANS[new_values["plan_name"]]
            client["assigned_public_ip"] = new_values["assigned_public_ip"] if "_IP" in new_values["plan_name"] else None
            command(f"ont modify {client['port']} {client['onu_id']} ont-lineprofile-id {client['wan'][0]['line_profile']}")
            command(f"ont modify {client['port']} {client['onu_id']} ont-srvprofile-id {client['wan'][0]['srv_profile']}")
            command("quit")
            add_service(comm, command, client)
            quit()
            return "success message {}"
          
      else:
            return "error message {}"