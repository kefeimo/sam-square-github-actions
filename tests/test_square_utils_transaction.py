import unittest
from squareup.square_utils import SquareClient, SquareCatalogUtils, SquareTransactionUtils
from tests.data_test import DfItemLib, ListPlan


class TestSquareTransactionUtils(unittest.TestCase):

    df_item_lib = DfItemLib.df_item_lib
    square_client = SquareClient.create(env="test")
    dict_plan = ListPlan().plan_as_dict_test    # note: this dict is not static, i.e., ids might change
    transaction_util = SquareTransactionUtils(square_client)

    def test_create_transaction_test(self):
        # to-do: make it more stringent: check the item variations id in the transaction
        results = self.transaction_util.create_transaction_test(self.dict_plan, date_hour_str="2020-10-10 7:00:00")
        result_is_success = [obj.is_success() for obj in results]
        self.assertTrue(all(result_is_success))

    def test_create_transaction(self):
        results = self.transaction_util.create_transaction(self.dict_plan)
        self.assertEqual(results, [])
