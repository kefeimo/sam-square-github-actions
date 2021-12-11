from squareup_api.square_utils import SquareClient, SquareCatalogUtils, SquareTransactionUtils
from data_demo import DfItemLib, ListPlan
import json


def init_square_item_library(df_item_lib) -> "Dataframe":
    # Use case demo
    square_client = SquareClient.create(env="test")
    catalog_util = SquareCatalogUtils(square_client)

    catalog_util.clear_catalog()
    df_item_lib_w_ids = catalog_util.create_item_library(df_item_lib)
    return df_item_lib_w_ids


def create_transaction() -> "transaction_info_list: empty":
    # Use case demo
    square_client = SquareClient.create(env="test")
    transaction_util = SquareTransactionUtils(square_client)
    return transaction_util.create_transaction(ListPlan().plan_as_dict_test)


def create_transaction_test() -> "transaction_info_list":
    # Use case demo
    # result_body = [obj.body for obj in results]
    # result_is_success = [obj.is_success() for obj in results]
    square_client = SquareClient.create(env="test")
    transaction_util = SquareTransactionUtils(square_client)
    results_trans = transaction_util.create_transaction_test(
        ListPlan().plan_as_dict_test, date_hour_str="2020-10-10 7:00:00"
    )
    return results_trans


# Press the green button in the gutter to run the script.
if __name__ == "__main__":

    # demo 1
    print("====demo 1: init_square_item_library====")
    df_lib = init_square_item_library(df_item_lib=DfItemLib.df_item_lib)
    # print("item library", df_lib)
    # Pretty Print JSON
    json_data = df_lib.to_json()
    obj = json.loads(json_data)
    json_formatted_str = json.dumps(obj, indent=2)
    print("item library", json_formatted_str)

    # demo 2
    print("====demo 2: create_transaction====")
    results = create_transaction()
    print("create_transaction result", results)

    # demo 3
    print("====demo 3: create_transaction_test====")
    results = create_transaction_test()
    print("create_transaction_test result", results)
    result_body = [obj.body for obj in results]
    print("create_transaction_test result_body", result_body)
    result_is_success = [obj.is_success() for obj in results]
    print("create_transaction_test status", result_is_success)
