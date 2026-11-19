from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response

from .models import Dht11
from .serializers import DHT11serialize

import telebot

def test(request):
    return HttpResponse("je suis lotfi")


def dashboard(request):
    return render(request, 'DHT/dashboard.html')


@api_view(['GET'])
def Dlist(request):
    all_data = Dht11.objects.order_by('-date')[:50]
    data = DHT11serialize(all_data, many=True).data
    return Response({'data': data})


class Dhtviews(generics.CreateAPIView):
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize

    def perform_create(self, serializer):
        data = serializer.save()
        temperature = data.temp

        if temperature > 25:
            message = f"Alerte ! Temperature = {temperature} °C"

            try:
                send_mail(
                    subject="Alerte Temperature",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=["lotfi.ai8627@gmail.com"],
                    fail_silently=False
                )
                print(">>> Mail envoye", flush=True)
            except Exception as e:
                print(">>> ERREUR MAIL :", repr(e), flush=True)

            try:
                bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
                bot.send_message(settings.TELEGRAM_CHAT_ID, message)
                print(">>> Telegram envoye", flush=True)
            except Exception as e:
                print(">>> ERREUR TELEGRAM :", repr(e), flush=True)