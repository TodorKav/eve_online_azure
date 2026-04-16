from rest_framework import serializers

from eve.industry.models import Categories, Groups, MarketGroups, Types, MarketPrices, CorporationsWithLPStores, \
    CorporationsLpItemTypes


class CategoriesListApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class GroupsListApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'

class GroupsListNestedApiSerializer(serializers.ModelSerializer):
    category_id = CategoriesListApiSerializer(read_only=True)
    class Meta:
        model = Groups
        fields = '__all__'

class MarketGroupListApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketGroups
        fields = '__all__'

class TypesListApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = '__all__'

class TypesListSmallApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = ['type_id', 'name',]

class TypesListNestedApiSerializer(serializers.ModelSerializer):
    group_id = GroupsListApiSerializer(read_only=True)
    market_group_id = MarketGroupListApiSerializer(read_only=True)
    class Meta:
        model = Types
        fields = '__all__'

class MarketPricesListApiSerializer(serializers.ModelSerializer):
    type_id = TypesListApiSerializer(read_only=True)
    class Meta:
        model = MarketPrices
        fields = '__all__'

class  CorporationsWithLPStoresListApiSerializer(serializers.ModelSerializer):
    types = TypesListSmallApiSerializer(source='type_id', many=True, read_only=True)
    class Meta:
        model = CorporationsWithLPStores
        fields = ['corporation_id', 'description', 'home_station_id', 'name', 'ticker', 'war_eligible', 'types']

class  CorporationsWithLPStoresSmallListApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporationsWithLPStores
        fields = ['corporation_id', 'name', 'ticker', ]

class CorporationsLpItemTypesListApiSerializer(serializers.ModelSerializer):
    types = TypesListSmallApiSerializer(source='type_id', read_only=True)
    class Meta:
        model = CorporationsLpItemTypes
        fields = ['corporation_id', 'ak_cost', 'isk_cost', 'lp_cost', 'offer_id', 'quantity', 'material_cost', 'required', 'types']

class ItemSerializer(serializers.Serializer):
    type_id = serializers.IntegerField(source='type_id_id')
    name = serializers.CharField(source='type_id.name')
    corporation = serializers.CharField(source='corporation_id.name')
    lp_cost = serializers.IntegerField()
    isk_cost = serializers.FloatField()
    required = serializers.CharField()
    material_cost = serializers.FloatField()
    quantity = serializers.IntegerField()
    adjusted_price = serializers.SerializerMethodField()
    price_pro_lp = serializers.FloatField()

    def get_adjusted_price(self, obj) -> float|None:
        try:
            return obj.type_id.market_prices.adjusted_price
        except AttributeError:
            return None