import json
import re
from pathlib import Path

from tool.Tool_general import log_message


def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Error decoding JSON in {file_path}.", doc=file_path, pos=0)
    except Exception as e:
        raise Exception(f"An error occurred while loading {file_path}: {str(e)}")


def filter_custom_report(custom_report, excluded_fields):
    return {k: v for k, v in custom_report.items() if k not in excluded_fields}


def get_flat_report_as_key_value(folder_path):
    suite_json_path = Path(folder_path) / 'json' / 'suite.json'
    # print(suite_json_path)
    try:
        data = load_json(suite_json_path)
        report_summary_default = data.get('reportSummary', {}).get('Default', {})
        custom_report_default = data.get('customReport', {}).get('Default', {})

        # 统计载波个数
        nr_count, lte_count ,w_count, g_count, nb_count = count_rat_information(suite_json_path)

        # 合并所有数据为平级结构（键值对）
        key_value_pairs = {**report_summary_default,
                           **custom_report_default,
                           "num_nr": nr_count,
                           "num_lte": lte_count,
                           "num_w": w_count,
                           "num_g": g_count,
                           "num_nb": nb_count,
                           # "NR_LTE_all_count": lte_count+nr_count
                           }

        excluded_fields = {
            "JCAT version",
            "MJE Properties",
            "MJE early console",
            "MJE version: ",
            "STP RPV_FULL_TX_14-stp_test_P1A resource beans",
            "Test data beans",
            "Working Directory",
            "endTimeInMillis",
            "error",
            "testEngine",
            "startTimeInMillis",
            "Host data report",
            "maxproc",
            "Jenkins build",
            "STP RPV_FULL_TX_14-stp resource beans"
        }
        key_value_pairs = filter_custom_report(key_value_pairs, excluded_fields)

        return key_value_pairs

    except FileNotFoundError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def getInfo_from_suiteJson(folder_path):
    return get_flat_report_as_key_value(folder_path)


def get_carrier_info(json_file_path):
    try:
        data = load_json(json_file_path)
        if 'testcases' in data:
            testcases = data['testcases']
            if '2' in testcases:
                item_2 = testcases['2']
                if 'additionalInfo' in item_2:
                    return json.dumps(item_2['additionalInfo'])
                else:
                    log_message("item 2 中没有 additionalInfo 元素")
                    return None
            else:
                log_message("testcases 中没有 2 元素")
                return None
        else:
            log_message("JSON 中没有 testcases 元素")
            return None
    except FileNotFoundError:
        log_message(Warning(f"File {json_file_path} not found."))
        return None
    except json.JSONDecodeError:
        log_message(Warning(f"Error decoding JSON in {json_file_path}."))
        return None
    except Exception:
        log_message(Warning(f"An error occurred while loading {json_file_path}."))
        return None


def count_rat_information(suite_json_path):
    additional_info = get_carrier_info(suite_json_path)
    if additional_info:
        nr_count = len(re.findall(r'RAT = NR', additional_info))
        lte_count = len(re.findall(r'RAT = LTE', additional_info))
        w_count = len(re.findall(r'RAT = WCDMA', additional_info))
        g_count = len(re.findall(r'RAT = GSM', additional_info))
        nb_count = len(re.findall(r'RAT = NBIOT', additional_info))
    else:
        nr_count = 0
        lte_count = 0
        w_count = 0
        g_count = 0
        nb_count = 0
    return nr_count, lte_count, w_count, g_count, nb_count

## UT
# if __name__ == "__main__":
#     json_path = Path('C:\\Users\\test\\Desktop\\log2csv\\src\\data\\20240625180855\\json\\suite.json')
#     print(get_carrier_info(json_path))
#     print(count_rat_information(get_carrier_info(json_path)))
#     key_value_data = get_flat_report_as_key_value(Path('C:\\Users\\test\\Desktop\\log2csv\\src\\data\\20240625180855'))
#     print(json.dumps(key_value_data, indent=4))