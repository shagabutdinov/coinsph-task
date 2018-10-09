from enum import Enum
from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction


class Currencies(Enum):
    """List of currencies available for project."""

    USD = "US Dollar"
    PHP = "Phillipine Peso"
    RUB = "Russian Rouble"


class Account(models.Model):
    """An individual account that holds money with given currency for owner."""

    id = models.CharField(max_length=128, primary_key=True)
    owner = models.CharField(max_length=256)

    balance = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0.0,
    )

    currency = models.CharField(
        max_length=128,
        choices=[(currency.name, currency.value) for currency in Currencies],
    )


class PaymentDirections(Enum):
    """The direction of payment."""

    OUTGOING = "outgoing"
    INCOMING = "incoming"


class Payment(models.Model):
    """Transaction that represent money transfer from one user to another."""

    account = models.ForeignKey(
        Account,
        related_name='account',
        on_delete=models.CASCADE,
    )

    from_account = models.ForeignKey(
        Account,
        related_name='from_account',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
    )

    to_account = models.ForeignKey(
        Account,
        related_name='to_account',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
    )

    direction = models.CharField(
        max_length=128,
        choices=[
            (dir.name, dir.value) for dir in PaymentDirections
        ],
    )

    amount = models.DecimalField(max_digits=16, decimal_places=2)

    def clean(self):
        self.ensure_amount_is_positive()
        self.ensure_from_or_to_account_present()
        self.ensure_from_and_to_account_not_present_together()
        self.ensure_to_account_is_set_for_outgoing()
        self.ensure_from_account_is_set_for_incoming()
        self.ensure_accounts_currencies_are_same()
        self.ensure_accounts_are_not_same()

    def ensure_amount_is_positive(self):
        if self.amount > 0:
            return

        raise ValidationError({
            'amount': 'Amount should be positve number',
        })

    def ensure_from_or_to_account_present(self):
        if self.from_account is not None:
            return

        if self.to_account is not None:
            return

        raise ValidationError({
            'from_account': '"From account" or "To account" can not be empty',
        })

    def ensure_from_and_to_account_not_present_together(self):
        if self.from_account is None:
            return

        if self.to_account is None:
            return

        raise ValidationError({
            'from_account':
                '"From account" and "To account" can be set together',
        })

    def ensure_to_account_is_set_for_outgoing(self):
        if self.direction != PaymentDirections.OUTGOING.name:
            return

        if self.to_account is not None:
            return

        raise ValidationError({
            'to_account':
                '"To account" should not be empty for outgoing payment',
        })

    def ensure_from_account_is_set_for_incoming(self):
        if self.direction != PaymentDirections.INCOMING.name:
            return

        if self.from_account is not None:
            return

        raise ValidationError({
            'from_account':
                '"From account" should not be empty for incoming payment',
        })

    def ensure_accounts_currencies_are_same(self):
        if self.direction == PaymentDirections.INCOMING.name:
            if self.account.currency == self.from_account.currency:
                return

        if self.direction == PaymentDirections.OUTGOING.name:
            if self.account.currency == self.to_account.currency:
                return

        raise ValidationError({
            'account':
                'Account should have same currency as "From" or "To" account',
        })

    def ensure_accounts_are_not_same(self):
        if self.direction == PaymentDirections.INCOMING.name:
            if self.account.id != self.from_account.id:
                return

        if self.direction == PaymentDirections.OUTGOING.name:
            if self.account.id != self.to_account.id:
                return

        raise ValidationError({
            'account': 'Accounts can not be same',
        })


def send_transaction(from_account_id, to_account_id, amount):
    """
    Sends transaction from one user to another.

    Args:
        from_account_id (str): sender of transaction
        to_account_id (str): receiver of transaction
        amount (float): amount of transaction, should be positive

    Returns:
        (Payment, Payment) Tuple with two created payments

    Raises:
        ValidationError: An error occured creating payments
    """
    with transaction.atomic():
        from_account = Account.objects.select_for_update().get(
            id=from_account_id,
        )

        to_account = Account.objects.select_for_update().get(
            id=to_account_id,
        )

        outgoing_payment = Payment(
            account=from_account,
            to_account=to_account,
            direction=PaymentDirections.OUTGOING.name,
            amount=amount,
        )

        outgoing_payment.full_clean()
        outgoing_payment.save()

        incoming_payment = Payment(
            account=to_account,
            from_account=from_account,
            direction=PaymentDirections.INCOMING.name,
            amount=amount,
        )

        incoming_payment.full_clean()
        incoming_payment.save()

        if from_account.balance < amount:
            raise ValidationError({
                'from_account': 'Insufficient funds',
            })

        from_account.balance -= Decimal(amount)
        from_account.save()

        to_account.balance += Decimal(amount)
        to_account.save()

    return (outgoing_payment, incoming_payment)
