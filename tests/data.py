import pandas as pd
from datetime import datetime
from squareup.square_utils import SquareClient, SquareCatalogUtils


class DfItemLib:
    """
    item library template in Pandas dataframe
    """
    df_item_lib = pd.DataFrame({
        "item_header": ["item_header_test", "item_header_test_2"] * 2,
        "variation_id": ["XXX"] * 4,
        "variation_name": ["variation_name_test", "variation_name_test_2",
                           "variation_name_test_3", "variation_name_test_4"],
        "item_id": ["XXX"] * 4,
        "item_name": ["item_name_test", "item_name_test_2"] * 2,
        "category_id": ["XXX"] * 4,
        "category_name": ["category_name_test", "category_name_test_2"] * 2,
        "variation_amount": ["100", "101"] * 2,
        "variation_currency": ["USD"] * 4,
        "item_description": [f"test item, created at {datetime.now()}"] * 4,
        "variation_id_inner": ["#XXXX#"] * 4
    })


class ListPlan:
    plan_as_dict_test: dict

    def __init__(self):
        square_client = SquareClient.create(env="test")
        catalog_util = SquareCatalogUtils(square_client)
        # catalog_util = SquareCatalogUtils()
        # catalog_util.create_item_library(DfItemLib.df_item_lib)
        item_variations = catalog_util.get_item_catalogs().get("item_variation")
        # variation_ids = catalog_util.df_item_lib.variation_id.values
        # print(variation_ids)
        variation_ids = [obj.get("id") for obj in item_variations \
                         if obj.get("item_variation_data").get('pricing_type') == 'FIXED_PRICING']

        # transaction_plan (hard coded for testing)
        plan_as_dict_test = {'2020-10-10 7:00:00':
                        [(302,[variation_ids[0], variation_ids[3], variation_ids[3]]),
                         (201,[variation_ids[2], variation_ids[1]]),
                         (402,[variation_ids[1], variation_ids[1],variation_ids[2], variation_ids[0]])]}
        self.plan_as_dict_test = plan_as_dict_test
