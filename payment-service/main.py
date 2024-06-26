# from fastapi import FastAPI, HTTPException
# from .producers import publish_payment_success, publish_payment_failed
# from .database import database
# from sqlalchemy import select
# from .models import Payment, Ride
# from .schemas import PaymentSchema
# from asyncpg.exceptions import UniqueViolationError
# from fastapi.middleware.cors import CORSMiddleware

# app= FastAPI(title='MicroCab payment-service')

# # Add CORS middleware to allow cross-origin requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=True,
#     allow_methods=['*']      
#     )

# # Defines functions for application to run before startup
# @app.on_event('startup')
# async def startup():
#     # Connect to database
#     await database.connect()
# # Defines functions for application to run before shutdown
# @app.on_event('shutdown')
# async def shutdown():
#     # Disconnect to database
#     await database.disconnect()

# # Root route for probing the application during startup
# @app.get('/')
# async def app_probe():
#     return {'message':'success'}

# # Endpoint to simulate payment success
# @app.post('/api/v1/payment/success/', summary='Endpoint to simulate payment success')
# async def payment_success(schema:PaymentSchema):
#     ride_query= select(Ride.c.id, Ride.c.fare, Ride.c.user_id).where(Ride.c.id==schema.ride_id)
#     ride= await database.fetch_one(ride_query)
#     if not ride:
#          raise HTTPException(detail='ride not found', status_code=404)
#     query= Payment.insert().values(ride_id=schema.ride_id, amount=ride.fare, user_id=ride.user_id)
#     try:
#         await database.execute(query)
#     except UniqueViolationError:
#         return {'message':'ride already paid for'}
#     await publish_payment_success({'ride_id':schema.ride_id, 'user_id':ride.user_id, 'driver_id': ride.driver_id, 'amount':ride.fare})
#     return {'message':'payment successful'}


# # Endpoint to simulate payment success
# @app.post('/api/v1/payment/failed/', summary='Endpoint to simulate payment failure')
# async def payment_failed(schema:PaymentSchema):
#     ride_query= select(Ride.c.id, Ride.c.user_id).where(Ride.c.id==schema.ride_id)
#     ride= await database.fetch_one(ride_query)
#     if not ride:
#          raise HTTPException(detail='ride not found', status_code=404)
#     await publish_payment_failed({'ride_id':schema.ride_id, 'user_id':ride.user_id})
#     return {'message':'payment failed'}


from __future__ import annotations
import fastapi_csrf_protect.exceptions, json
import typing, json

import ormar.exceptions

from API.exceptions import exceptions as api_exceptions
from API import settings, models
from API.settings import application
import pydantic, stripe.error, logging, fastapi, datetime
from fastapi_csrf_protect import CsrfProtect

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_API_SECRET



class PaymentValidationForm(pydantic.BaseModel):

    subscription_id: int
    purchaser_id: int
    amount: int
    currency: typing.Literal["usd", "eur", "rub"]


def create_payment_session(customer, subscription) -> stripe.checkout.Session:
    return stripe.checkout.Session.create(

            api_key=getattr(settings, 'STRIPE_API_SECRET'),
            success_url=settings.SUCCESS_SESSION_URL,
            cancel_url=settings.CANCEL_SESSION_URL,

            line_items=[{
                "price": stripe.Price.retrieve(api_key=settings.STRIPE_API_SECRET, id=subscription.price_id),
                "quantity": 1,
            }],
            metadata={
                "subscription_id": subscription.id,
                "subscription_name": subscription.subscription_name,
                "purchaser_id": customer.id,
                "date": datetime.datetime.now(),
            },
            customer=customer.stripe_customer_id,
            mode="subscription",
            after_expiration=None)


@application.post(path='/payment/session/', response_class=fastapi.responses.JSONResponse)
async def start_payment_session(request: fastapi.Request, csrf_protect: CsrfProtect = fastapi.Depends()):
    """
    / * Creates Payment Session for the Subscription and returns
    """
    try:
        csrf_protect.validate_csrf_in_cookies(request=request) if csrf_protect is not None else None
        subscription = await models.Subscription.objects.get(
        id=int(request.query_params.get('subscription_id')))

        customer = await models.StripeCustomer.objects.get(
        id=int(request.query_params.get('customer_id')))
        session = create_payment_session(customer=customer, subscription=subscription)

        return fastapi.responses.JSONResponse(content={'session_id': session.get('id')},
        headers={'Content-Type': 'application/json'}, status_code=201)

    except(stripe.error.InvalidRequestError, AssertionError, KeyError, AttributeError, TypeError) as exception:
        logger.debug('[PAYMENT SESSION EXCEPTION]: %s' % exception)
        raise api_exceptions.PaymentSessionFailed(reason=exception.args)

    except(ormar.exceptions.NoMatch):
        return fastapi.HTTPException(status_code=404)


def create_payment_intent(purchaser: models.StripeCustomer, payment_object: PaymentValidationForm) -> dict:

    try:
        intent = stripe.PaymentIntent.create(
                api_key=settings.STRIPE_API_SECRET,
                amount=payment_object.dict().get('amount'),

                payment_method_types=['card'],
                currency=payment_object.dict().get('currency'),

                customer=stripe.Customer.retrieve(id=purchaser.stripe_customer_id,
                api_key=settings.STRIPE_API_SECRET),

                metadata={
                    'subscription_id': payment_object.dict().get('subscription_id'),
                    'amount': payment_object.dict().get('amount'),
                    'purchaser_id': purchaser.id
                },
            )
        intent.metadata.update({'payment_intent_id': intent.get('client_secret')})
        return {'payment_intent_id': intent.get('client_secret'), 'payment_id': intent.id}
    except(stripe.error.InvalidRequestError, KeyError, AttributeError, TypeError) as exception:
        raise exception



@application.post(path='/payment/intent/', response_class=fastapi.responses.JSONResponse) # amount, subscription_id
async def get_payment_intent(request: fastapi.Request, payment_credentials: str = fastapi.Form(), csrf_protect: CsrfProtect = fastapi.Depends()):
        try:
            customer = await models.StripeCustomer.objects.get(id=int(request.query_params.get('customer_id')))
            csrf_protect.validate_csrf_in_cookies(request=request) if csrf_protect is not None else None

            intent_secret = create_payment_intent(
            payment_object=PaymentValidationForm(**json.loads(payment_credentials)), purchaser=customer)
            return fastapi.responses.JSONResponse(intent_secret, status_code=200)

        except(pydantic.ValidationError, stripe.error.InvalidRequestError, AttributeError, KeyError, TypeError) as exception:
            logger.error('[PAYMENT INTENT EXCEPTION]: %s' % exception)
            return fastapi.HTTPException(status_code=400, detail='Invalid Credentials.')

        except(fastapi_csrf_protect.exceptions.CsrfProtectError):
            return fastapi.HTTPException(status_code=403)

        except(stripe.error.PermissionError) as exception:
            logger.error('Looks Like Stripe Token is Expired, or try to use secret if you have not still')
            raise exception

@application.get(path='/get/all/user/payments/')
async def get_all_payments(request: fastapi.Request):
    try:
        queryset = await models.StripeCustomer.objects.filter(
        id=request.query_params.get('customer_id')).first().select_related('payments')
        return fastapi.responses.Response(json.dumps({'queryset': queryset}), status_code=200)
    except(ormar.NoMatch):
        return fastapi.HTTPException(status_code=404)
