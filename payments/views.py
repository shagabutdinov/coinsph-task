import json

from django.http import JsonResponse, HttpResponseServerError
from payments.models import Payment, Account, send_transaction


def accounts(request):
    """Displays all accounts in the application"""

    # consider we have small application and can afford show all accounts
    accounts = Account.objects.all()
    return JsonResponse(list(accounts.values()), safe=False)


def payments(request):
    """Entrypoint payments method"""

    if request.method == 'POST':
        return create_payment(request)

    return payments_list(request)


def payments_list(request):
    """Displays all payments in the application"""

    # consider we have small application and can afford show all payments
    payments = Payment.objects.all()
    return JsonResponse(list(payments.values()), safe=False)


def create_payment(request):
    """Sends money from one user to another"""

    data = json.loads(request.body)

    try:
        (outgoing_payment, incoming_payment) = send_transaction(
            data['from_account'],
            data['to_account'],
            data['amount'],
        )

        return JsonResponse({'ok': True}, safe=False)

    except KeyError:
        return HttpResponseServerError('Malformed data!')
