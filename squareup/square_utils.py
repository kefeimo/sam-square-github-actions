from square.client import Client
import pandas as pd
from pandas.core.frame import DataFrame

import time
import uuid

import itertools

from config import *


class _SquareClientFactory:

    def __init__(self, access_token, environment, square_version):
        self.__access_token = access_token  # use environment variable
        self.__environment = environment  # use environment variable
        self.__square_version = square_version  # use environment variable

        self.square_client = self._square_connect()

    def _square_connect(self):
        client: Client = Client(
            access_token=self.__access_token,
            environment=self.__environment,
            square_version=self.__square_version,
        )
        # note: no need to test connection. It is just a wrapper on Rest API (i.e., Requests)
        return client


class SquareClient:
    @staticmethod
    def create(env: str = "dev") -> Client:
        """
        Create square client (i.e. connector, a wrapper on Rest API, like Requests)
        :param env: str, "dev", "test", "prod"
        :return:
        """
        if env == "dev":
            client = SquareClient._square_client_dev()
        elif env == "test":
            client = SquareClient._square_client_test()
        elif env == "production":
            raise Exception("To-do: add SquareClient._square_client_prod()")
        else:
            raise ValueError("`env` not in ['dev', 'test', 'prod']")
        return client

    @staticmethod
    def _square_client_test() -> Client:
        client: Client = _SquareClientFactory(access_token=SQUARE_TOKEN_TEST,
                                              environment=SQUARE_ENV_TEST,
                                              square_version=SQUARE_VERSION_TEST).square_client
        return client

    @staticmethod
    def _square_client_dev() -> Client:
        client: Client = _SquareClientFactory(access_token=SQUARE_TOKEN_DEV,
                                              environment=SQUARE_ENV_DEV,
                                              square_version=SQUARE_VERSION_DEV).square_client
        return client

    @staticmethod
    def get_location_ids(client: Client) -> list:
        """
        Get location ids
        :return:
        """
        result = client.locations.list_locations()
        if result.errors:
            print(result)
            raise Exception(result)
        location_id: list = [obj.get("id") for obj in result.body.get("locations")]
        return location_id


class SquareCatalogUtils:

    def __init__(self, square_client: Client):
        self.square_client = square_client
        self.df_item_lib: DataFrame

    def clear_catalog(self, catalog_types: str = None) -> None:
        """
        Clear catalogs (i.e., category, item, item_variation) in Square item library.
        :param catalog_types: str, "CATEGORY" or "ITEM", or "ITEM_VARIATION"
        :return: None
        Note: if types=None, all the catalogs will be deleted
        """
        # step 1 Catalog -> List catalog
        client = self.square_client
        result = client.catalog.list_catalog(types=catalog_types)
        if result.errors:
            print(result)
            raise Exception(result)

        # step 2 Catalog -> Delete catalog object.
        if result.body.get("objects") is None:  # early return
            return
        # retrieve the ids
        ids_to_del = [obj.get("id") for obj in result.body.get("objects")]
        for id_ in ids_to_del:
            result = client.catalog.delete_catalog_object(
                object_id=id_
            )
        if result.errors:
            print(result)
            raise Exception(result)

    def _insert_category(self, category_name: str) -> str:
        client = self.square_client
        result = client.catalog.upsert_catalog_object(
            body={
                "idempotency_key": str(uuid.uuid1()),
                "object": {
                    "type": "CATEGORY",
                    "id": "#" + category_name,  # placeholder, NOT the real id
                    "category_data": {
                        "name": category_name
                    }}})
        if result.errors:
            print(result)
            raise Exception(result)
        category_id: str = result.body.get("catalog_object").get("id")
        return category_id

    def _insert_item(self, item_name: str, item_description: str, category_id: str = None):
        client = self.square_client
        result = client.catalog.upsert_catalog_object(
            body={
                "idempotency_key": str(uuid.uuid1()),
                "object": {
                    "type": "ITEM",
                    "id": "#" + item_name,
                    "item_data": {
                        "name": item_name,
                        "description": item_description,
                        "category_id": category_id
                    }}}
        )
        if result.errors:
            print(result)
            raise Exception(result)
        item_id: str = result.body.get("catalog_object").get("id")
        return item_id

    def _insert_variation(self, variation_name: str, item_id=None, variation_amount=None, variation_currency=None):
        client = self.square_client
        result = client.catalog.upsert_catalog_object(
            body={
                "idempotency_key": str(uuid.uuid1()),
                "object": {
                    "type": "ITEM_VARIATION",
                    "id": "#" + variation_name,  #
                    "item_variation_data": {
                        "name": variation_name,
                        "item_id": item_id,

                        "pricing_type": "FIXED_PRICING",
                        "price_money": {
                            "amount": int(variation_amount),
                            "currency": variation_currency
                        }}}}
        )
        if result.errors:
            print(result)
            raise Exception(result)
        variation_id: str = result.body.get("catalog_object").get("id")
        return variation_id

    def create_item_library(self, df_item_lib: DataFrame) -> DataFrame:
        """
        Create item library in Square from a Pandas Dataframe,
        in 3 steps:
            1. insert category
            2. insert item
            3. insert variation
        :param df_item_lib: Dataframe, item library template (without catalog ids)
        :return: df: Dataframe, (with catalog ids)
        EX:
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
        """
        df = df_item_lib.copy()
        # category
        df_category = df[["category_id", "category_name"]].groupby("category_name").first().reset_index()
        df_category["category_id"] = df_category.apply(lambda x: self._insert_category(x["category_name"]), axis=1)
        # merge back
        df = pd.merge(df.drop("category_id", axis=1), df_category, on="category_name", how='left')

        # item
        df_item = df[["item_id", "item_name", "item_description", "category_id"]].groupby(
            "item_name").first().reset_index()
        df_item["item_id"] = df_item.apply(lambda x: self._insert_item(x["item_name"],
                                                                  x["item_description"],
                                                                  x["category_id"],
                                                                  ), axis=1)
        # merge back
        df = pd.merge(df.drop("item_id", axis=1),
                      df_item.drop(["item_description", "category_id"], axis=1), on="item_name", how='left')

        # variation
        df_variation = df[["variation_id", "variation_name", "item_id", "category_id",
                           "variation_amount", "variation_currency", ]].copy()
        df_variation["variation_id"] = df_variation.apply(lambda x: self._insert_variation(x["variation_name"],
                                                                                      x["item_id"],
                                                                                      x["variation_amount"],
                                                                                      x["variation_currency"],
                                                                                      ), axis=1)
        # merge back
        df = pd.merge(df.drop("variation_id", axis=1),
                      df_variation.drop(["category_id", "variation_amount", "variation_currency"], axis=1),
                      on=["variation_name", "item_id"], how='left')
        self.df_item_lib = df
        return df

    def get_item_catalogs(self) -> dict:
        """
        A wrapper on catalog.list_catalog()
        :param self:
        :return:
        """
        catalog_dict = {"category": None,
                        "item": None,
                        "item_variation": None}
        client = self.square_client
        result = client.catalog.list_catalog()

        if result.errors:  # only test when there is no error
            print(result)
            raise Exception(result)

        catalog_dict["category"] = [obj for obj in result.body.get("objects") \
                                    if obj.get("type") == 'CATEGORY']
        catalog_dict["item"] = [obj for obj in result.body.get("objects") \
                                if obj.get("type") == 'ITEM']
        item_variation_list = [obj.get("item_data").get("variations") for obj in result.body.get("objects")\
                               if obj.get("type") == 'ITEM']
        item_variation_list_flat = (itertools.chain(*item_variation_list))
        catalog_dict["item_variation"] = item_variation_list_flat

        return catalog_dict


class SquareTransactionUtils:

    def __init__(self, square_client: Client):
        self.square_client = square_client

        self.transaction_plan: list = []    # self._get_trans_plans_for_the_hour(dict_plan)

    def _create_order(self, line_items, location_id):

        data = {"idempotency_key": str(uuid.uuid1()),
                "order": {"location_id": location_id,
                          "line_items": line_items
                          }
                }

        result = self.square_client.orders.create_order(body=data)
        if result.errors:
            print(result)
            raise Exception(result)
        return result

    def _create_payment(self, result_create_order):
        total_amount = result_create_order.body.get("order").get("total_money").get("amount")
        order_id = result_create_order.body.get('order').get('id')

        data = {"amount_money": {"currency": "USD", "amount": total_amount},
                "idempotency_key": str(uuid.uuid1()),
                "source_id": "cnon:card-nonce-ok",
                "order_id": order_id}

        result = self.square_client.payments.create_payment(body=data)
        if result.errors:
            print(result)
            raise Exception(result)
        return result

    @staticmethod
    def _get_trans_plans_for_the_hour(dict_plan, tz=None, date_hour_str=None, plan_w_minu=False) -> list:
        # timezone
        if tz is None:
            os.environ['TZ'] = 'America/Los_Angeles'
        if date_hour_str is None:
            try:
                date_hour_str = time.strftime('%Y-%m-%d %-H:00:00')
            except Exception as e:
                print(e)
                date_hour_str = time.strftime('%Y-%m-%d %#H:00:00')  # use %#H no leading zeros
            print("Use TIME NOW: ", time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print(f"Use TIME Custom at: {date_hour_str}")

        # get plans
        trans_plans: list = dict_plan.get(date_hour_str)
        if trans_plans is not None:
            print(f"Transaction plan: {trans_plans}")
            if plan_w_minu:
                return trans_plans
            else:
                return [trans for minu, trans in trans_plans]  # to-do: redundant: this is always the case
        else:
            print("No transaction exists in the plan")
            return []

    def _verify_transaction_item(self):
        list_plan: list = self.transaction_plan
        result = self.square_client.catalog.list_catalog(types="ITEM_VARIATION")
        if result.errors:
            print(result)
            raise Exception(result)
        variation_ids = [obj.get("id") for obj in result.body.get("objects")]

        items_for_transaction = set(itertools.chain(*list_plan))  # flatten
        for variation_id in items_for_transaction:
            if variation_id not in variation_ids:
                raise Exception(f"variation_id {variation_id} not in item library")

    def _create_transaction_workflow(self) -> list:
        list_plan: list = self.transaction_plan
        if not list_plan:
            return []

        # verify
        # self._verify_transaction_item()
        # execution
        location_id: str = SquareClient.get_location_ids(self.square_client)[0] # to-do: avoid assume only one location
        result_transaction_list: list = []
        for item_list in list_plan:
            line_items = [{"quantity": "1", "catalog_object_id": item} for item in item_list]
            result_create_order = self._create_order(line_items, location_id)
            result_create_payment = self._create_payment(result_create_order)
            result_transaction_list.append(result_create_payment)
        return result_transaction_list

    def create_transaction_test(self, dict_plan, date_hour_str="2020-10-10 7:00:00") -> list:
        self.transaction_plan = self._get_trans_plans_for_the_hour(dict_plan, date_hour_str=date_hour_str)
        results = self._create_transaction_workflow()
        print("create_transaction_test FINISHED")
        return results

    def create_transaction(self, dict_plan) -> list:
        """
        Create transaction workflow based on plan
        :param dict_plan: see the format below
        :param date_hour_str: see the format below
        :return:
        EX: dict_plan format
            plan_as_dict_test = {'2020-10-10 7:00:00':
                        [(302,[variation_ids[0], variation_ids[3], variation_ids[3]]),
                         (201,[variation_ids[2], variation_ids[1]]),
                         (402,[variation_ids[1], variation_ids[1],variation_ids[2], variation_ids[0]])]}
        """
        self.transaction_plan = self._get_trans_plans_for_the_hour(dict_plan)
        results = self._create_transaction_workflow()
        print("create_transaction_test FINISHED")
        return results
