from rest_framework import serializers

class BookSerializer(serializers.Serializer):
    id=serializers.IntegerField(label = "Enter Book ID")
    title=serializers.CharField(label = "Enter Book Title")
    author=serializers.CharField(label = "Enter Book Author Names")


class NMEASerializer(serializers.Serializer):
    time = serializers.CharField(label = "Time")
    PRN = serializers.CharField(label = "PRN")
    C_N0 = serializers.CharField(label = "C_N0")
    ConstellationType = serializers.CharField(label = "ConstellationType")
    SVID = serializers.CharField(label = "SVID")
    Azimuth = serializers.CharField(label = "Azimuth")
    Elevation = serializers.CharField(label = "Elevation")