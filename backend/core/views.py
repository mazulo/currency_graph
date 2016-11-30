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
        """
        Create multiples currencies based on the range of dates
        """
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

        return

    def daterange(self, start_date, end_date):
        """
        Helper function to create a range of dates
        """
        for n in range(int((end_date - start_date).days)):
            yield start_date + timezone.timedelta(n)

    def get_data(self, context):
        """
        Override method to get the data to be returned
        """
        context = super().get_data(context)

        # Remove the view, added by generic.TemplateView
        context.pop('view')

        current_date = timezone.datetime.date(timezone.datetime.now())
        dates = [
            current_date - timezone.timedelta(days=x) for x in range(1, 8)
        ]
        first_date = dates[-1]

        base = self.request.GET.get('base')

        query = self.get_queryset(base, [first_date, current_date])

        if query.exists():

            query_count = query.count()

            if query_count < 7:
                start_date = query.first().date
                new_dates = [
                    date for date in self.daterange(start_date, current_date)
                ]

                self.create_currencies(
                    base,
                    new_dates,
                    current_date,
                    start_date
                )

            query = self.get_queryset(base, [first_date, current_date])
            context['currencies'] = self.serialize_objects(query)
            # context['currencies'] = query
        else:
            self.create_currencies(
                base,
                dates,
                current_date,
                first_date,
            )
            currency_queryset = self.get_queryset(
                base,
                [first_date, current_date]
            )
            context['currencies'] = self.serialize_objects(currency_queryset)
            # context['currencies'] = currency_queryset

        return context

    def get_json_api_response(self, base, date):
        """
        Return the json response from fixer.io
        """
        return requests.get(
            settings.API_URL.format(base=base, date=date.isoformat())
        ).json()

    def get_queryset(self, base, range_dates):
        return Currency.objects.filter(
            base=base,
            date__range=range_dates
        ).order_by('date')

    def render_to_response(self, context, **response_kwargs):
        """
        Use the .render_to_response method to return the
        render_to_json_response from the mixin
        """
        return self.render_to_json_response(context, **response_kwargs)

    def serialize_objects(self, objects):

        to_serialize = objects.only('date', 'value')

        return serializers.serialize(
            'python',
            to_serialize,
            fields=('date', 'value'),
        )
