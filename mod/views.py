from rest_framework.response import Response
from rest_framework import generics
from django.http import HttpResponse
from dotenv import load_dotenv
import os

load_dotenv()

from mod.scripts.MC import modifyClient

class MOD(generics.GenericAPIView):
  def get(self, req):
    status_code = 200
    response_text = "ms_running"
    return HttpResponse(response_text, status=status_code)
  def post(self,req):
    if req.META['HTTP_CONEXT_KEY'] == os.environ["CONEXT_KEY"]:
      status_code = 200
      tp,modify,data,new_values = req.data.values()
      if tp == "a":
        res = modifyClient(modify, data, new_values)
        return Response({"message":res["message"], "data":res["client"],"error": res["error"]})
      return Response({"message":"Manual Action Needed", "data":{},})
    else:
      return HttpResponse("Bad Request to server", status=400)