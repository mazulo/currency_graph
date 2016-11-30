from django.conf import settings
from django.core import serializers
from django.views import generic
from django.utils import timezone

from .mixins import JSONResponseMixin
from .models import Currency

import requests


class IndexView(generic.TemplateView):

    template_name = 'core/index.html'


class CurrencyView(JSONResponseMixin, generic.TemplateView):
    symbol_target = 'BRL'

    def create_currencies(self, base, dates, current_date, first_date):
        currency_instances = []

        for date in dates:
            json_response = self.get_json_api_response(base, date)
            currency_instances.append(
                Currency(
                    date=date,
                    base=base,
                    symbol_target=self.symbol_target,
                    value=json_response['rates']['BRL'],
                )
            )
        Currency.objects.bulk_create(currency_instances)

        return Currency.objects.filter(
            base=base,
            date__range=[first_date, current_date],
        ).order_by('date')

    def get_data(self, context):
        context = super().get_data(context)

        context.pop('view')

        current_date = timezone.datetime.date(timezone.datetime.now())
        dates = [
            current_date - timezone.timedelta(days=x) for x in range(1, 8)
        ]
        first_date = dates[-1]

        base = self.request.GET.get('base')

        query = Currency.objects.filter(
            base=base,
            date__range=[first_date, current_date]
        )

        if query.exists():

            if query.count() < 7:
                json_response = self.get_json_api_response(base, current_date)
                Currency.objects.create(
                    date=current_date,
                    base=base,
                    symbol_target=self.symbol_target,
                    value=json_response['rates']['BRL']
                )

            query = query.order_by('date')
            context['currencies'] = self.serialize_objects(query)
            # context['currencies'] = query
        else:
            currency_queryset = self.create_currencies(
                base,
                dates,
                current_date,
                first_date,
            )
            context['currencies'] = self.serialize_objects(currency_queryset)
            # context['currencies'] = currency_queryset

        return context

    def get_json_api_response(self, base, date):
        return requests.get(
            settings.API_URL.format(base=base, date=date.isoformat())
        ).json()

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def serialize_objects(self, objects):

        to_serialize = objects.only('date', 'value')

        return serializers.serialize(
            'python',
            to_serialize,
            fields=('date', 'value'),
        )
