from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Wallet, Transaction, Product
from .serializers import *
import requests, os
from django.shortcuts import get_object_or_404

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'msg': 'User registered'})
    return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fund(request):
    wallet = Wallet.objects.get(user=request.user)
    amount = float(request.data['amount'])
    wallet.balance += amount
    wallet.save()
    Transaction.objects.create(user=request.user, txn_type='FUND', amount=amount, balance_after=wallet.balance)
    return Response({'balance': wallet.balance})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay(request):
    sender = request.user
    receiver = get_object_or_404(User, username=request.data['to'])
    amount = float(request.data['amount'])

    sender_wallet = Wallet.objects.get(user=sender)
    receiver_wallet = Wallet.objects.get(user=receiver)

    if sender_wallet.balance < amount:
        return Response({'error': 'Insufficient balance'}, status=400)

    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    sender_wallet.save()
    receiver_wallet.save()

    Transaction.objects.create(user=sender, txn_type='PAY', amount=amount, balance_after=sender_wallet.balance)
    Transaction.objects.create(user=receiver, txn_type='RECEIVE', amount=amount, balance_after=receiver_wallet.balance)

    return Response({'balance': sender_wallet.balance})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def balance(request):
    wallet = Wallet.objects.get(user=request.user)
    currency = request.GET.get('currency', 'INR')
    balance = wallet.balance
    if currency != 'INR':
        api_key = os.getenv('CURRENCY_API_KEY')
        res = requests.get(f'https://api.currencyapi.com/v3/latest?apikey={api_key}&currencies={currency}')
        rate = res.json()['data'][currency]['value']
        balance *= rate
    return Response({'balance': balance, 'currency': currency})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request):
    txns = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    serializer = TransactionSerializer(txns, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'msg': 'Product added'})
    return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_product(request):
    product = get_object_or_404(Product, id=request.data['product_id'])
    wallet = Wallet.objects.get(user=request.user)

    if wallet.balance < product.price:
        return Response({'error': 'Insufficient funds'}, status=400)

    wallet.balance -= product.price
    wallet.save()
    Transaction.objects.create(user=request.user, txn_type='BUY', amount=product.price, balance_after=wallet.balance)
    return Response({'msg': f'Bought {product.name}', 'balance': wallet.balance})
