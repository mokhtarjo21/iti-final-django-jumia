import stripe
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Jumia Order',
                    },
                    'unit_amount': 2000,  # total in cents
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url='http://localhost:3000/success',  # your React URL
        cancel_url='http://localhost:3000/cancel',
    )
    return Response({'url': session.url})
