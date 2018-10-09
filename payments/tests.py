import json

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse

from payments.models import Payment, Account, Currencies, PaymentDirections
from payments.models import send_transaction


def create_alice_account():
    return Account.objects.create(
        id='test_alice_account',
        owner='alice',
        balance=100,
        currency=Currencies.PHP.name,
    )


def create_bob_account():
    return Account.objects.create(
        id='test_bob_account',
        owner='bob',
        balance=100,
        currency=Currencies.PHP.name,
    )


class PaymentTestCase(TestCase):
    def setUp(self):
        self.alice_account = create_alice_account()
        self.bob_account = create_bob_account()

        self.payment_data = {
            'account': self.alice_account,
            'amount': 10,
        }

    def test_is_created(self):
        payment = Payment(
            **self.payment_data,
            to_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
        )

        payment.full_clean()
        payment.save()

        payments = Payment.objects.filter(account=self.alice_account.id)
        self.assertEqual(len(payments.all()), 1)

    def test_not_creates_without_target_account_id(self):
        payment = Payment(**self.payment_data)
        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_negative_amount(self):
        payment = Payment(
            account=self.alice_account,
            to_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
            amount=-10,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_zero_amount(self):
        payment = Payment(
            account=self.alice_account,
            to_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
            amount=0,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_to_account_and_incoming(self):
        payment = Payment(
            **self.payment_data,
            to_account=self.bob_account,
            direction=PaymentDirections.INCOMING.name,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_from_account_and_incoming(self):
        payment = Payment(
            **self.payment_data,
            from_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_from_account_and_to_account(self):
        payment = Payment(
            **self.payment_data,
            from_account=self.alice_account,
            to_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_accounts_with_different_currencies(self):
        self.bob_account.currency = Currencies.USD
        self.bob_account.save()

        payment = Payment(
            **self.payment_data,
            to_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)

    def test_not_creates_for_same_accounts(self):
        payment = Payment(
            **self.payment_data,
            to_account=self.alice_account,
            direction=PaymentDirections.OUTGOING.name,
        )

        self.assertRaises(ValidationError, Payment.full_clean, payment)


class SendTransactionTestCase(TestCase):
    def setUp(self):
        self.alice_account = create_alice_account()
        self.bob_account = create_bob_account()

    def test_creates_two_payments(self):
        send_transaction(self.alice_account.id, self.bob_account.id, 100)

        payments = Payment.objects.filter(account__in=[
            self.alice_account.id,
            self.bob_account.id,
        ])

        self.assertEqual(len(payments.all()), 2)

    def test_creates_outgoing_payment(self):
        send_transaction(self.alice_account.id, self.bob_account.id, 100)

        payment = Payment.objects.get(to_account=self.bob_account.id)
        self.assertEqual(payment.account_id, self.alice_account.id)
        self.assertEqual(payment.to_account_id, self.bob_account.id)
        self.assertEqual(payment.direction, PaymentDirections.OUTGOING.name)
        self.assertEqual(payment.amount, 100)

    def test_creates_incoming_payment(self):
        send_transaction(self.alice_account.id, self.bob_account.id, 100)

        payment = Payment.objects.get(from_account=self.alice_account.id)
        self.assertEqual(payment.account_id, self.bob_account.id)
        self.assertEqual(payment.from_account_id, self.alice_account.id)
        self.assertEqual(payment.direction, PaymentDirections.INCOMING.name)
        self.assertEqual(payment.amount, 100)

    def test_raises_on_insufficient_funds(self):
        self.assertRaises(
            ValidationError,
            send_transaction,
            self.alice_account.id,
            self.bob_account.id,
            200,
        )

    def test_updates_from_account_balance(self):
        send_transaction(self.alice_account.id, self.bob_account.id, 10)
        self.alice_account.refresh_from_db()
        self.assertEqual(self.alice_account.balance, 90.0)

    def test_updates_to_account_balance(self):
        send_transaction(self.alice_account.id, self.bob_account.id, 10)
        self.bob_account.refresh_from_db()
        self.assertEqual(self.bob_account.balance, 110.0)


class AccountsViewTestCase(TestCase):
    def test_lists_accounts(self):
        create_alice_account()
        response = self.client.get(reverse('accounts'))
        data = json.loads(response.content)
        account = None

        for item in data:
            if item['id'] == 'test_alice_account':
                account = item

        self.assertEqual(account, {
            'id': 'test_alice_account',
            'owner': 'alice',
            'balance': '100.00',
            'currency': 'PHP',
        })


class PaymentsViewTestCase(TestCase):
    def setUp(self):
        self.alice_account = create_alice_account()
        self.bob_account = create_bob_account()

    def test_lists_payments(self):
        Payment.objects.create(
            account=self.alice_account,
            to_account=self.bob_account,
            direction=PaymentDirections.OUTGOING.name,
            amount=100,
        )

        response = self.client.get(reverse('payments'))
        data = json.loads(response.content)
        payment = None

        for item in data:
            if item['account_id'] == 'test_alice_account':
                payment = item

        del payment['id']

        self.assertEqual(payment, {
            'account_id': 'test_alice_account',
            'from_account_id': None,
            'to_account_id': 'test_bob_account',
            'direction': 'OUTGOING',
            'amount': '100.00',
        })

    def test_creates_payments(self):
        data = json.dumps({
            'from_account': self.alice_account.id,
            'to_account': self.bob_account.id,
            'amount': 25.0,
        })

        response = self.client.generic('POST', reverse('payments'), data)
        self.assertEqual(json.loads(response.content)['ok'], True)
