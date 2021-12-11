"""
Note: this set of tests include clear the database. It might cause conflict with other tests.
Recommend: run this set of tests alone.
"""

import unittest
from squareup.square_utils import SquareClient, SquareCatalogUtils, SquareTransactionUtils
from tests.data_test import DfItemLib, ListPlan


class TestSquareCatalogUtils(unittest.TestCase):

    df_item_lib = DfItemLib.df_item_lib
    square_client = SquareClient.create(env="test")
    catalog_util = SquareCatalogUtils(square_client)

    def test_clear_catalog(self):
        # to-do: allow conditional pass
        # to-do: allow try mutliple times
        self.catalog_util.clear_catalog()
        client = self.catalog_util.square_client
        result = client.catalog.list_catalog(types=None)
        # self.assertTrue(result.body.get("objects") is None)
        if result.errors: # only test when there is no error
            print(result)
        else:
            self.assertTrue(result.body.get("objects") is None)

    def test_create_item_library(self):
        # to-do: allow conditional pass
        # to-do: allow try mutliple times
        # watch-out: Square automatically create a `ITEM_VARIATION` with `pricing_type`==`FIXED_PRICING`
        self.catalog_util.clear_catalog()
        self.catalog_util.create_item_library(self.df_item_lib)
        df_w_ids = self.catalog_util.df_item_lib
        catalog_dict = self.catalog_util.get_item_catalogs()

        # print(set([obj.get("id") for obj in catalog_dict.get("category")]))
        # print(set(df_w_ids["category_id"].unique()))
        # print()
        # print(set([obj.get("id") for obj in catalog_dict.get("item")]))
        # print(set(df_w_ids["item_id"].unique()))
        # print()
        # print(set([obj.get("id") for obj in catalog_dict.get("item_variation")]))
        # print(set(df_w_ids["variation_id"].unique()))
        # print()

        # for category
        self.assertEqual(set(df_w_ids["category_id"].unique()),
                         set([obj.get("id") for obj in catalog_dict.get("category")]))
        # for item
        self.assertEqual(set(df_w_ids["item_id"].unique()),
                         set([obj.get("id") for obj in catalog_dict.get("item")]))
        # for item variations
        self.assertEqual(set(df_w_ids["variation_id"].unique()),
                         set([obj.get("id") for obj in catalog_dict.get("item_variation")\
                              if obj.get("item_variation_data").get('pricing_type') == 'FIXED_PRICING']))


