from django.apps import apps
from django.db import models



class CreatedAtMixin(models.Model):
    created_at = models.DateField(auto_now=True, blank=True, null=True)
    class Meta:
        abstract = True


class CreatedAtDateTimeMixin(models.Model):
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    class Meta:
        abstract = True


class PublishedMixin(models.Model):
    published = models.BooleanField(default=False)
    class Meta:
        abstract = True


class RequiredItemsMixin:
    @staticmethod
    def display(queryset):
        Types = apps.get_model('industry', 'Types') # lazy loading to avoid circular imports

        ##################################
        # creating a type list, the goal is to get all objects from CorporationsLpItemTypes.required_items with one request
        all_type_ids = set()
        for obj in queryset:
            if obj.required_items:
                for content in obj.required_items:
                    all_type_ids.add(content.get('type_id'))

        # type_object_dict is a dictionary with key: types_id and the value is a class Types object
        type_object_dict = {t.type_id: t for t in Types.objects.filter(type_id__in=all_type_ids).select_related('market_prices')}
        ####################################

        for obj in queryset:
            if not obj.required_items:
                setattr(obj, 'required', None)
            else:
                content_list = []
                material_cost = 0
                for content in obj.required_items:
                    quantity = content.get('quantity')
                    type_object = type_object_dict.get(content.get('type_id'))

                    ############################################
                    # due to inconsistencies in the database it is possible to have class Types objects without corresponding
                    # MarketPrices object. The goal here is to avoid crashes, because of such inconsistencies.
                    mc = getattr(type_object, 'market_prices', None)
                    if mc:
                        if material_cost is not None:
                            material_cost += type_object.market_prices.adjusted_price * quantity
                            # print(type_object.market_prices.adjusted_price)
                    else:
                        material_cost = None
                        # print(type_object.type_id)
                        # print(obj.type_id.name)
                    ###############################################


                    content_list.append(f'Item: {type_object.name} quantity: {quantity}.')
                setattr(obj, 'required', ', '.join(content_list))
                setattr(obj, 'material_cost', material_cost)

        return queryset