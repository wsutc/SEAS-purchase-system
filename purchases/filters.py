import django_filters

from .models import Tracker


class TrackerFilter(django_filters.FilterSet):
    class Meta:
        model = Tracker
        fields = ["carrier"]
