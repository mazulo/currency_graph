from django.db import models
from django.utils.translation import ugettext_lazy as _


class CreateUpdateModel(models.Model):

    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'atualizado em',
        auto_now=True
    )

    class Meta:
        abstract = True


class Currency(CreateUpdateModel):

    date = models.DateField(verbose_name=_('currency date'))
    base = models.CharField(
        verbose_name=_('currency base'),
        max_length=3)
    symbol_target = models.CharField(
        verbose_name=_('currency target'),
        max_length=3
    )
    value = models.DecimalField(
        verbose_name=_('currency value'),
        decimal_places=2,
        max_digits=10,
    )

    def __str__(self):
        return '{base} -> {symbol_target}: {value}'.format(
            base=self.base,
            symbol_target=self.symbol_target,
            value=self.value
        )
