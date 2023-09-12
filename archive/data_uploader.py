import json
import math
import time
from algoliasearch.search_client import SearchClient
from datetime import datetime, timedelta


client = SearchClient.create('SF0IKHXEOM', '68ff5251ad7e59a3da88bd09b7994d53')
index = client.init_index('test_arXiv')


dataset = 'archive/arxiv-metadata-oai-snapshot.json'
test0 = 'archive/arxiv test0.json'
test1 = 'archive/arxiv test1.json'
test2 = 'archive/arxiv test2.json'
dataset_out = 'archive/arxiv.json'


def batch_upload(list_of_json_objects):
    index.save_objects(list_of_json_objects, {'autoGenerateObjectIDIfNotExist': True})


def json_batch_process(file_path, batch_size, upload):
    # upload = True or False
    with open(file_path, 'r') as file:
        all_lines = file.readlines()

    batch_count = math.ceil(len(all_lines)/batch_size)
    print('batch_count:', batch_count)

    for batch in range(batch_count):
        start_index = batch * batch_size
        end_index = min((batch + 1) * batch_size, len(all_lines))
        current_batch = [json.loads(line) for line in all_lines[start_index:end_index]]

        if not upload:
            print('batch', batch)
            print()
            continue
        elif upload:
            batch_upload(current_batch)
            print('uploaded batch', batch)
            print()
            time.sleep(0.5)


def delete_elements(jdict, waste_elements):
    return {k: v for k, v in jdict.items() if k not in waste_elements}


def object_id(jdict):
    new_dict = {"objectID": jdict.pop("id")}  # Remove "id" key and assign its value to "objectID"
    new_dict.update(jdict)  # Add the remaining key-value pairs
    return new_dict


def delete_outdated(jdict):
    versions = jdict.get("versions", [])

    if not versions:
        return jdict

    # Extract the date from the first version
    first_version = versions[0]
    first_version_date = datetime.strptime(first_version["created"], '%a, %d %b %Y %H:%M:%S %Z')

    # Calculate the date 3 years ago from today
    years_ago = datetime.now() - timedelta(days=365 * 1)

    if first_version_date < years_ago:
        # If the latest version is more than 3 years old, return nothing
        print('an outdated paper is deleted')
        return None
    else:
        jdict.update({"first_version_date": str(first_version_date)})
        return jdict


def ignore_authors(jdict):
    authors = jdict.get("authors_parsed")
    if authors and len(authors) > 50:
        limited_authors = authors[:50]
        more_authors_count = len(authors) - 50
        jdict["authors_parsed"] = limited_authors
        jdict["message"] = f"Here are the first 50 authors, and {more_authors_count} more not shown."
    return jdict


def modify_elements(file_path, target_path, mode=None, waste=None):

    if mode is None:
        print('in function modify_elements, the mode is not specified')
        return

    if type(mode) is not str:
        print('in function modify_elements, the mode is not specified')
        return

    print('reading the input file...')
    with open(file_path, 'r') as file:
        lines = file.readlines()

    print('processing')
    if mode == 'delete_elements':
        modified_lines = [json.dumps(delete_elements(json.loads(line), waste)) + '\n' for line in lines]

    if mode == 'object_id':
        modified_lines = [json.dumps(object_id(json.loads(line))) + '\n' for line in lines]

    if mode == 'delete_outdated':
        modified_lines = []
        for line in lines:
            if delete_outdated(json.loads(line)) is None:
                continue
            else:
                modified_lines.append(json.dumps(delete_outdated(json.loads(line))))
                modified_lines.append('\n')

    if mode == 'ignore_authors':
        modified_lines = [json.dumps(ignore_authors(json.loads(line))) + '\n' for line in lines]

    print('writing the output file...')
    with open(target_path, 'w') as file:
        file.writelines(modified_lines)


# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
json_batch_process(dataset_out, 1000, True)


'''waste = ['submitter', 'authors', 'comments', 'report-no', 'license', 'update_date', 'versions']
modify_elements(dataset, dataset_out, mode='delete_outdated')
modify_elements(dataset_out, dataset_out, mode='delete_elements', waste=waste)
modify_elements(dataset_out, dataset_out, mode='object_id')
modify_elements(dataset_out, dataset_out, mode='ignore_authors')'''

# modify_elements(dataset_out, dataset_out, mode='delete_outdated')
# modify_elements(test0, test0, mode='delete_elements', waste=waste)
