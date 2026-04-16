from django.db.models import Q, ExpressionWrapper, FloatField, Value, F, Model
from django.db.models.functions import Coalesce, NullIf
from django.views.generic import ListView
from django.views.generic.edit import BaseFormView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from eve.industry.forms import SearchForm
from eve.industry.models import CorporationsLpItemTypes, Categories, Groups, MarketGroups, Types, MarketPrices, \
    CorporationsWithLPStores
from eve.industry.serializers import CategoriesListApiSerializer, MarketGroupListApiSerializer, \
    GroupsListNestedApiSerializer, TypesListNestedApiSerializer, MarketPricesListApiSerializer, \
    CorporationsWithLPStoresListApiSerializer, CorporationsLpItemTypesListApiSerializer, ItemSerializer


# Create your views here.


class ItemList(ListView, BaseFormView):
    template_name = 'industry/items_list.html'
    model = CorporationsLpItemTypes
    form_class = SearchForm
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(Q(type_id__name__icontains=q) | Q(corporation_id__name=q))


        return queryset.select_related('type_id', 'type_id__market_prices', 'corporation_id',).annotate(
            price_pro_lp=ExpressionWrapper(
                (
                    Coalesce(F('type_id__market_prices__adjusted_price'), Value(0.0)) * F('quantity')
                    - Coalesce(F('isk_cost'), Value(0.0))
                    - Coalesce(F('material_cost'), Value(0.0))
                ) / NullIf(Coalesce(F('lp_cost'), Value(1.0)), Value(0.0)),
                output_field=FloatField()
            )
        ).order_by(F('price_pro_lp').desc(nulls_last=True))

    def get_initial(self):
        initial = super().get_initial()
        initial['q'] = self.request.GET.get('q')
        return initial

class ItemPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'

class CategoriesListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Categories.objects.all().order_by('category_id')
    serializer_class = CategoriesListApiSerializer
    pagination_class = ItemPagination

class GroupsListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Groups.objects.select_related('category_id').all().order_by('group_id')
    serializer_class = GroupsListNestedApiSerializer
    pagination_class = ItemPagination

class MarketGroupsListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = MarketGroups.objects.all().order_by('market_group_id')
    serializer_class = MarketGroupListApiSerializer
    pagination_class = ItemPagination

class TypesListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Types.objects.select_related('group_id', 'market_group_id').all().order_by('type_id')
    serializer_class = TypesListNestedApiSerializer
    pagination_class = ItemPagination

class MarketPricesListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = MarketPrices.objects.select_related('type_id').all().order_by('type_id')
    serializer_class = MarketPricesListApiSerializer
    pagination_class = ItemPagination

class CorporationsWithLPStoresListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = CorporationsWithLPStores.objects.prefetch_related('type_id').order_by('corporation_id')
    serializer_class = CorporationsWithLPStoresListApiSerializer
    pagination_class = ItemPagination

class CorporationsLpItemTypesListApiView(ListAPIView):
    permission_classes =  [IsAuthenticated, ]
    queryset = CorporationsLpItemTypes.objects.select_related('type_id', 'corporation_id').all().order_by('corporation_id')
    serializer_class = CorporationsLpItemTypesListApiSerializer
    pagination_class = ItemPagination

class ItemListApiView(ListAPIView):
    permission_classes =  [IsAuthenticated, ]
    serializer_class = ItemSerializer
    pagination_class = ItemPagination

    def get_queryset(self):
        # same queryset logic as your existing get_queryset()
        queryset = CorporationsLpItemTypes.objects.select_related(
            'type_id', 'type_id__market_prices', 'corporation_id'
        ).annotate(
            price_pro_lp=ExpressionWrapper(
                (
                    Coalesce(F('type_id__market_prices__adjusted_price'), Value(0.0)) * F('quantity')
                    - Coalesce(F('isk_cost'), Value(0.0))
                    - Coalesce(F('material_cost'), Value(0.0))
                ) / NullIf(Coalesce(F('lp_cost'), Value(1.0)), Value(0.0)),
                output_field=FloatField()
            )
        ).order_by(F('price_pro_lp').desc(nulls_last=True))

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(type_id__name__icontains=q) | Q(corporation_id__name=q)
            )

        return queryset