from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializer import *

# Create your views here.
class BookApiView(APIView):
    serializer_class = BookSerializer
    def get(self,request):
        allBooks=Book.objects.all().values()
        return Response({"Message": "List of books", "Book List":allBooks})


    def post(self,request):
        print("Request data is: ", request.data)
        serializer_obj = BookSerializer(data=request.data)
        if(serializer_obj.is_valid()):
            Book.objects.create(id=serializer_obj.data.get("id"),
                                title=serializer_obj.data.get("title"),
                                author=serializer_obj.data.get("author"))

        book=Book.objects.all().filter(id=request.data["id"]).values()
        return Response({"Message": "New Book Added!", "Book":book})
    



class NMEAApiView(APIView):
    serializer_class = NMEASerializer
    def get(self,request):
        allNMEA = NMEA.objects.all().values()
        return Response({"Naviagtion Message" : "List of NMEA", "NMEA List": allNMEA})
    

    def post(self,request):
        print("Request data is: ", request.data)
        serializer_obj = NMEASerializer(data=request.data)
        if(serializer_obj.is_valid()):
            NMEA.objects.create(time=serializer_obj.data.get("time"),
                                PRN=serializer_obj.data.get("PRN"),
                                C_N0=serializer_obj.data.get("C_N0"),
                                ConstellationType=serializer_obj.data.get("ConstellationType"),
                                SVID=serializer_obj.data.get("SVID"),
                                Azimuth=serializer_obj.data.get("Azimuth"),
                                Elevation=serializer_obj.data.get("Elevation"))
                                
            nmea = NMEA.objects.all().filter(time=request.data["time"]).values()
            return Response({"Message": "Navigation Message:", "NMEA": nmea})




    