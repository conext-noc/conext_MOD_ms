import os
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework import generics
from django.http import HttpResponse
from mod.scripts.MC import client_modify

load_dotenv()


class MOD(generics.GenericAPIView):
    def get(self, _):
        status_code = 200
        response_text = "ms_running"
        return HttpResponse(response_text, status=status_code)

    def post(self, req):
        if req.META["HTTP_CONEXT_KEY"] == os.environ["CONEXT_KEY"]:
            data = req.data
            if data["type"] == "a":
                res = client_modify(data)
                return Response(res)
            return Response(
                {"message": "Manual Action Needed", "data": {}, "error": False}
            )
        return HttpResponse("Bad Request to server", status=400)


class MODDashboard(generics.GenericAPIView):
    def get(self, _):
        status_code = 200
        response_text = "ms_running"
        return HttpResponse(response_text, status=status_code)

    def post(self, req):
        data = req.data
        if data["API_KEY"] == os.environ["API_KEY"]:
            if data["type"] == "m":
                res = client_modify(data)
                return Response(res)
            return Response(
                {"message": "Manual Action Needed", "data": {}, "error": False}
            )
        return HttpResponse("Bad Request to server", status=400)
