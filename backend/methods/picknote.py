from methods.redis import MyRedis
import requests
import json

redis = MyRedis()


def picknote_saving_logic(picknote, token):
    if not redis.get(picknote):
        # get picknote from api with header
        headers = {"Authorization": token}

        response = requests.get(
            f"http://192.168.0.245:9095/api/Picknote/picknoteitemWithoutValidation?PicknoteNo={picknote}",
            headers=headers,
        )
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get("data")

            if data is not None:
                if isinstance(data, str):
                    print("Data is string")
                    data = json.loads(data)

                # filter data, extract only name and batch, and store in list of json
                filtered_data = [
                    {
                        "batch": item["batch"] if item.get("batch") else None,
                        "product_name": item["product_name"]
                        if item.get("product_name")
                        else None,
                        "product_code": item["product_code"]
                        if item.get("product_code")
                        else None,
                    }
                    for item in data
                    if item.get("name") and item.get("batch")
                ]
                redis.set(picknote, json.dumps(filtered_data))

                return True

            else:
                return False
        else:
            return False
    else:
        return True
